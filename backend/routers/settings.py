from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import SettingsBase, SettingsResponse
from backend.models import Setting
from backend.database import get_db

router = APIRouter()

# دریافت تنظیمات
@router.get("/", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Setting).first()
    if not settings:
        # بازگشت تنظیمات پیش‌فرض در صورت نبود تنظیمات
        return {
            "id": 0,
            "language": "en",
            "theme": "light",
            "enable_notifications": True,
            "created_at": None,
            "updated_at": None
        }
    return settings

# به‌روزرسانی تنظیمات
@router.put("/", response_model=SettingsResponse)
def update_settings(new_settings: SettingsBase, db: Session = Depends(get_db)):
    settings = db.query(Setting).first()
    if not settings:
        # ایجاد رکورد تنظیمات در صورت نبود آن
        settings = Setting(**new_settings.dict())
        db.add(settings)
    else:
        # به‌روزرسانی مقادیر تنظیمات
        settings.language = new_settings.language
        settings.theme = new_settings.theme
        settings.enable_notifications = new_settings.enable_notifications
    db.commit()
    db.refresh(settings)
    return settings
