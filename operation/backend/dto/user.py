from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    profile_pic: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
