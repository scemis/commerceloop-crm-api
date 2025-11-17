# api/users/routes.py
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.deps import get_db
from api.auth.deps import get_current_user  # ✅ единый источник авторизации
from api.users import crud
from api.users.schemas import SearchUserRequest, EditUserRequest

from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum
from core.logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["user"],
    dependencies=[Depends(get_current_user)]  # ✅ защита всего роутера, токен из Authorize / cookie
)

@router.get("/users/by-id/{userId}")
def read_user(
    request: Request,
    userId: int = 0,
    db: Session = Depends(get_db)
):
    obj = crud.get_user_by_id(db, userId)

    logger.info(
        f"[USER][GET_BY_ID] actor_id={request.state.user['id']} "
        f"target_user_id={userId} found={bool(obj)} ip={request.client.host}"
    )
    return obj


@router.get("/user/all", response_model=List[SearchUserRequest])
def list_employees(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 5
):
    rows = crud.list_users_joined(db, skip, limit)

    logger.info(
        f"[USER][LIST] actor_id={request.state.user['id']} "
        f"skip={skip} limit={limit} count={len(rows)} ip={request.client.host}"
    )

    return [
        SearchUserRequest(
            userId=u_.id,
            first_name=det.first_name,
            last_name=det.last_name,
            email=u_.email,
            phone=det.phone_number,
            created_at=det.created_at,
            description=u_.description,
            last_date_connection=u_.last_date_connection,
            role=role.role_name,
            country=det.country,
            city=det.city,
            date_of_birth=det.date_of_birth,
        )
        for u_, det, role in rows
    ]


@router.put("/user/edit/{userId}")
def edit_user(
    request: Request,
    userId: int = 0,
    editUserRequest: EditUserRequest | None = None,
    db: Session = Depends(get_db),
):
    crud.update_user(db, userId, editUserRequest)
    ip = request.client.host
    actor = request.state.user  

    fields = list(editUserRequest.model_dump(exclude_none=True).keys()) if editUserRequest else []
    logger.info(
        f"[USER][UPDATE] actor_id={actor['id']} "
        f"target_user_id={userId} "
        f"fields={fields} "
        f"ip={ip}"
    )
    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.edit,
                description=f"User {userId} updated fields {fields} from IP {ip}",
                entity=EntityEnum.users,
                emploee_id=actor["id"],
                user_id=userId,   
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "Connect user updated successfully"}

