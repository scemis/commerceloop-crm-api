from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.companies.models import Companis

def create_company(db: Session, data):
    obj = Companis(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def list_companies(db: Session, skip=0, limit=100):
    return db.query(Companis).offset(skip).limit(limit).all()

def get_company_by_id(db: Session, company_id: int):
    obj = db.query(Companis).filter(Companis.id == company_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail='Company not found')
    return obj

def search_by_name(db: Session, name: str | None):
    if name == '-':
        return db.query(Companis).all()
    return db.query(Companis).filter(Companis.firm_name.like(f"%{name}%")).all()
