from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import DomainCreate, DomainResponse
from backend.models import Domain
from backend.database import get_db

router = APIRouter()

# دریافت لیست دامنه‌ها
@router.get("/", response_model=list[DomainResponse])
def get_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    return domains

# اضافه کردن دامنه جدید
@router.post("/", response_model=DomainResponse)
def create_domain(domain: DomainCreate, db: Session = Depends(get_db)):
    # بررسی وجود نام دامنه تکراری
    if db.query(Domain).filter(Domain.name == domain.name).first():
        raise HTTPException(status_code=400, detail="Domain already exists")
    
    new_domain = Domain(
        name=domain.name,
        description=domain.description
    )
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)
    return new_domain

# ویرایش دامنه
@router.put("/{domain_id}", response_model=DomainResponse)
def update_domain(domain_id: int, domain: DomainCreate, db: Session = Depends(get_db)):
    db_domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db_domain.name = domain.name
    db_domain.description = domain.description
    db.commit()
    db.refresh(db_domain)
    return db_domain

# حذف دامنه
@router.delete("/{domain_id}")
def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    db_domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    db.delete(db_domain)
    db.commit()
    return {"message": "Domain deleted successfully"}
