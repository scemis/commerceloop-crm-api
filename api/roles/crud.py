from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.roles.models import Roles

def list_roles(db: Session, skip=0, limit=100):
    return db.query(Roles).offset(skip).limit(limit).all()

def create_role(db: Session, role_name: str):
    obj = Roles(role_name=role_name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_role_by_id(db: Session, role_id: int):
    obj = db.query(Roles).filter(Roles.id == role_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail='Role not found')
    return obj
