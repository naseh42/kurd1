from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import UserCreate, UserResponse
from backend.models import User
from backend.database import get_db

router = APIRouter()

# دریافت لیست کاربران
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# ایجاد کاربر جدید
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # چک کردن وجود نام کاربری یا UUID تکراری
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.uuid == user.uuid).first():
        raise HTTPException(status_code=400, detail="UUID already exists")
    
    new_user = User(
        username=user.username,
        uuid=user.uuid,
        traffic_limit=user.traffic_limit,
        usage_duration=user.usage_duration,
        simultaneous_connections=user.simultaneous_connections,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ویرایش اطلاعات کاربر
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.username = user.username
    db_user.uuid = user.uuid
    db_user.traffic_limit = user.traffic_limit
    db_user.usage_duration = user.usage_duration
    db_user.simultaneous_connections = user.simultaneous_connections
    db.commit()
    db.refresh(db_user)
    return db_user

# حذف کاربر
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
