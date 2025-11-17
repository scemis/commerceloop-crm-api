# api/auth/deps.py
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from sqlalchemy.orm import Session

from config import settings
from database import SessionLocal
# если модели пользователей лежат в другом месте — поправь импорт ниже
from api.users.models import Users

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db: Session) -> Optional[Users]:
    user = db.query(Users).filter(Users.email == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_pass):
        return None
    return user

def create_access_token(user: Users, expires_delta: timedelta) -> str:
    to_encode = {"email": user.email, "id": user.id, "role": user.role_id}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    request: Request,
    token: Annotated[Optional[str], Depends(oauth2_bearer)],
):
    # Читаем токен
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("email")
        user_id: int = payload.get("id")
        role: int = payload.get("role")

        if email is None or user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Could not validate user.")
        
        user_obj = {"email": email, "id": user_id, "role": role}
        request.state.user = user_obj

        return user_obj

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate user.")
