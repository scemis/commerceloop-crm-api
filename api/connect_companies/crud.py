from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.connect_companies.models import ConnectCompanis
from api.companies.models import Companis

def create_with_company(db: Session, worker_id: int, payload):
    company = Companis(
        firm_name=payload.firm_name,
        email=payload.email,
        phone=payload.phone,
        created_at=datetime.utcnow()
    )
    db.add(company); db.commit(); db.refresh(company)

    connect = ConnectCompanis(
        worker_id=worker_id,
        company_id=company.id,
        created_at=datetime.utcnow(),
        next_meeting=payload.next_meeting,
        is_approved=0,
        status=payload.status,
        description=payload.description
    )
    db.add(connect); db.commit(); db.refresh(connect)
    return connect

def get_by_id(db: Session, connect_company_id: int):
    obj = db.query(ConnectCompanis).filter(ConnectCompanis.id == connect_company_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail='Company Contact not found')
    return obj

def list_by_worker(db: Session, worker_id: int):
    return db.query(ConnectCompanis).filter(ConnectCompanis.worker_id == worker_id).all()

def list_potential(db: Session, skip=0, limit=5):
    # join для возврата витрины (как в старом коде)
    return (db.query(ConnectCompanis)
            .join(Companis, ConnectCompanis.company_id == Companis.id)
            .offset(skip).limit(limit).all())

def update_connect(db: Session, company_id_param: int, payload):
    # сохраняем прежнюю семантику: поиск по company_id
    obj = db.query(ConnectCompanis).filter(ConnectCompanis.company_id == company_id_param).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Connect company with id {company_id_param} not found")
    obj.next_meeting = payload.next_meeting
    obj.status = payload.status
    obj.description = payload.description
    obj.is_approved = 0 if payload.status.value == 'pending' else obj.is_approved
    obj.last_update = datetime.utcnow()
    db.commit(); db.refresh(obj)
    return obj
