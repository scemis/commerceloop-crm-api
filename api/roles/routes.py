from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user   # ✅ единый источник авторизации
from api.roles import crud
from api.roles.schemas import RoleBase

router = APIRouter(
    prefix="/auth",
    tags=["role"],
    dependencies=[Depends(get_current_user)]   # ✅ защита всего роутера
)

@router.get("/roles/all", response_model=List[RoleBase])
def list_roles(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.list_roles(db, skip, limit)

@router.post("/role/", status_code=201)
def create_role(db: Session = Depends(get_db), role: RoleBase = None):
    obj = crud.create_role(db, role.role_name)
    return obj

@router.get("/role/by-id/{role_id}", response_model=RoleBase)
def get_role(role_id: int = 0, db: Session = Depends(get_db)):
    return crud.get_role_by_id(db, role_id)
