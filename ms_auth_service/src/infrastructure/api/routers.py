from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.domain.schemas import UserLogin, UserRegister, TokenResponse, UserProfile
from src.infrastructure.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from src.infrastructure.storage import users, roles

router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invÃ¡lidas")
    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    existing = next((u for u in users if u["username"] == payload.username), None)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")
    new_user = {
        "id": len(users) + 1,
        "username": payload.username,
        "hashed_password": get_password_hash(payload.password),
        "role": payload.role,
        "created_at": datetime.utcnow().isoformat(),
    }
    users.append(new_user)
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "role": new_user["role"],
        "permissions": roles.get(new_user["role"], []),
    }

@router.post("/auth/logout")
async def logout():
    return {"status": "success", "message": "Logout realizado"}

@router.get("/auth/profile", response_model=UserProfile)
async def profile(user: UserProfile = Depends(get_current_user)):
    return user
