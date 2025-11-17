from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from core.deps import get_db
from core.config import settings
from core.security import hash_password, verify_password, create_access_token, get_current_user
from api.users.models import Users, PersonalDetails
from pydantic import BaseModel
from datetime import date

from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum
from core.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])

class CreateUserRequest(BaseModel):
    email: str
    description: str | None = None
    hashed_pass: str
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    city: str
    country: str
    phone: str
    role_id: int = 3

class Token(BaseModel):
    access_token: str
    token_type: str

from fastapi import Request
from core.logger import logger
from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum

@router.post("/employee/add", status_code=status.HTTP_201_CREATED)
def create_user(
    request: Request,
    db: Session = Depends(get_db),
    payload: CreateUserRequest | None = None
):
    if db.query(Users).filter(Users.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = Users(
        full_name=f"{payload.first_name} {payload.last_name}",
        email=payload.email,
        description=payload.description,
        hashed_pass=hash_password(payload.hashed_pass),
        role_id=payload.role_id,
    )
    db.add(user); db.commit(); db.refresh(user)

    details = PersonalDetails(
        user_id=user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        city=payload.city,
        country=payload.country,
        phone_number=payload.phone,
    )
    db.add(details); db.commit()

    ip = request.client.host
    logger.info(
        f"[USER][CREATE] actor_id={request.state.user['id'] if hasattr(request.state, 'user') else 'system'} "
        f"new_user_id={user.id} email='{user.email}' role_id={user.role_id} ip={ip}"
    )

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.create,
                description=f"Created user {user.id} ({user.email}) from {ip}",
                entity=EntityEnum.users,
                emploee_id=(request.state.user["id"] if hasattr(request.state, "user") else user.id),
                user_id=user.id,
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"message": "User created successfully", "user_id": user.id}


@router.post("/token", response_model=Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request and request.client else "unknown"
    now = datetime.utcnow().isoformat(timespec="seconds")

    user = db.query(Users).filter(Users.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_pass):
        logger.warning(
            f"[{now}] Failed login attempt | email={form.username} | ip={ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )

    logger.info(
        f"[{now}] Successful login | user_id={user.id} email={user.email} | ip={ip}"
    )

    token = create_access_token(
        {"email": user.email, "id": user.id, "role": user.role_id},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    try:
        activity_crud.create_activity_log(
            db,
            ActivityLogCreate(
                action=ActivityLogEnum.login,
                description=f"User logged in successfully from {ip}",
                entity=EntityEnum.users,
                emploee_id=user.id,
                user_id=user.id,
            ),
        )
    except Exception:
        logger.exception("Failed to write activity log to DB")

    return {"access_token": token, "token_type": "bearer"}
