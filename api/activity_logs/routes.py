from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user
from api.activity_logs import crud
from api.activity_logs.schemas import ActivityLogCreate, ActivityLogOut

router = APIRouter(
    prefix="/auth",
    tags=["activityLog"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/activityLog/add", response_model=dict)
def add_activity_log(
    activity_log: ActivityLogCreate,
    db: Session = Depends(get_db),
):
    obj = crud.create_activity_log(db, activity_log)
    return {"message": "Activity Log created successfully", "activity_log_id": obj.id}


@router.get("/activityLog/all", response_model=List[ActivityLogOut])
def list_activity_logs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.list_activity_logs(db, skip, limit)
