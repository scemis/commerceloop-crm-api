from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def hash_password(plain): return pwd_context.hash(plain)

def create_access_token(payload: dict, expires_delta: timedelta):
    to_encode = payload.copy()
    to_encode['exp'] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: Annotated[str, oauth2_scheme]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        required = ('email','id','role')
        if not all(k in payload for k in required):
            raise ValueError("bad payload")
        return {'email': payload['email'], 'id': payload['id'], 'role': payload['role']}
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
