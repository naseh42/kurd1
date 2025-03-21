from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Domain
from backend.utils.cert_manager import generate_certificate

router = APIRouter()

# افزودن دامنه جدید
@router.post("/")
def add_domain(domain_name: str, use_cdn: bool, use_reality: bool, db: Session = Depends(get_db)):
    try:
        # ایجاد دامنه جدید در پایگاه داده
        new_domain = Domain(name=domain_name, cdn=use_cdn, reality=use_reality)
        db.add(new_domain)
        db.commit()
        
        # دریافت گواهی SSL
        generate_certificate(domain_name)
        
        return {"message": "Domain added successfully", "domain": domain_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# حذف دامنه
@router.delete("/{domain_id}")
def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db.delete(domain)
    db.commit()
    return {"message": "Domain deleted successfully"}

# لیست تمام دامنه‌ها
@router.get("/")
def list_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    return domains

# تنظیمات پیشرفته برای دامنه
@router.put("/{domain_id}")
def update_domain_settings(domain_id: int, cdn: bool, reality: bool, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    domain.cdn = cdn
    domain.reality = reality
    db.commit()
    return {"message": "Domain settings updated successfully", "domain": domain.name}
