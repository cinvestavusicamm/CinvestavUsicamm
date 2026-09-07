from datetime import datetime, timedelta
from typing import Optional
import bcrypt

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.infrastructure.config import settings
from src.domain.schemas import UserProfile
from src.infrastructure.storage import users, get_password_hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = next((u for u in users if u["username"] == username), None)
    if user and verify_password(password, user["hashed_password"]):
        return user
    return None


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invÃ¡lido o expirado",
        )
    return payload


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProfile:
    payload = decode_access_token(token)
    return UserProfile(
        id=None,
        username=payload.get("sub"),
        role=payload.get("role", "student"),
        permissions=[],
    )
