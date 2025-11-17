from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.activity_logs.models import ActivityLogs
from api.activity_logs.schemas import ActivityLogCreate

def list_activity_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ActivityLogs).offset(skip).limit(limit).all()

def create_activity_log(db: Session, payload):
    obj = ActivityLogs(
        action=payload.action,
        description=payload.description,
        entity=payload.entity,
        emploee_id=payload.emploee_id,
        user_id=payload.user_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_activity_log_by_id(db: Session, activity_log_id: int):
    obj = db.query(ActivityLogs).filter(ActivityLogs.id == activity_log_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return obj