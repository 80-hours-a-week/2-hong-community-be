from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    profileImageUrl: Optional[str] = None
    createdAt: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    profileImageUrl: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    password: str