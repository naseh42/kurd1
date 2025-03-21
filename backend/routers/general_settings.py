from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import SettingsBase, SettingsResponse
from backend.database import get_db

router = APIRouter()

# تغییر زبان و سایر تنظیمات عمومی
@router.put("/language", response_model=SettingsResponse)
def update_language(language: str, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    if language not in ["fa", "en"]:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    settings.language = language
    db.commit()
    db.refresh(settings)
    return settings

@router.put("/theme", response_model=SettingsResponse)
def update_theme(theme: str, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    if theme not in ["light", "dark"]:
        raise HTTPException(status_code=400, detail="Invalid theme")
    
    settings.theme = theme
    db.commit()
    db.refresh(settings)
    return settings

# سایر تنظیمات عمومی (مثل اعلان‌ها)
@router.put("/notifications", response_model=SettingsResponse)
def update_notifications(enable: bool, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    settings.enable_notifications = enable
    db.commit()
    db.refresh(settings)
    return settings
