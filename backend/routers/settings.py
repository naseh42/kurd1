from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.utils.config_manager import add_inbound, update_port, restart_service
from backend.database import get_db

router = APIRouter()

# افزودن اینباند جدید
@router.post("/config/inbound")
def add_inbound_route(inbound_data: dict, db: Session = Depends(get_db)):
    try:
        add_inbound("/etc/xray/config.json", inbound_data)
        restart_service("xray")  # ری‌استارت سرویس Xray برای اعمال تغییرات
        return {"message": "Inbound added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# تغییر پورت اینباند
@router.put("/config/port")
def update_port_route(inbound_tag: str, new_port: int, db: Session = Depends(get_db)):
    try:
        update_port("/etc/xray/config.json", inbound_tag, new_port)
        restart_service("xray")  # ری‌استارت سرویس Xray
        return {"message": "Port updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# سایر قابلیت‌های کانفیگ‌ها (می‌توانیم موارد بیشتر اضافه کنیم)
