from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.utils.helpers import generate_uuid
from backend.utils.qr_code_generator import generate_qr_code

router = APIRouter()

# ایجاد کاربر جدید
@router.post("/")
def create_user(username: str, traffic_limit: int, usage_duration: int, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    uuid = generate_uuid()
    new_user = User(
        username=username,
        uuid=uuid,
        traffic_limit=traffic_limit,
        usage_duration=usage_duration,
        simultaneous_connections=1  # مقدار پیش‌فرض
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully", "uuid": uuid}

# نمایش اطلاعات کاربران
@router.get("/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# تمدید یا ویرایش کاربر
@router.put("/{user_id}")
def update_user(user_id: int, traffic_limit: int, usage_duration: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.traffic_limit = traffic_limit
    user.usage_duration = usage_duration
    db.commit()
    return {"message": "User updated successfully"}

# تولید لینک سابسکرپشن و QR Code
@router.get("/{user_id}/subscription")
def generate_subscription(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription_link = f"https://example.com/subscription/{user.uuid}"
    qr_code_image = generate_qr_code(subscription_link)
    
    return {"subscription_link": subscription_link, "qr_code": qr_code_image}

# حذف کاربر
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
