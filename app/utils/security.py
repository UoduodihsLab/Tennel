# app/utils/security.py

from datetime import datetime, timezone, timedelta
from typing import Dict

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict, expires_delta: int = 7):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Expired token")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
