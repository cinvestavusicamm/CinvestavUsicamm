from pydantic import BaseModel
from typing import List, Optional


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "student"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    id: Optional[int]
    username: str
    role: str
    permissions: List[str] = []
