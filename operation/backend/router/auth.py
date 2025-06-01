from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from model.database import get_db
from dto.user import UserCreate, UserLogin
from service.auth_service import create_user, authenticate_user
from core.security import (
    create_access_token, create_refresh_token,
    set_token_cookies, clear_token_cookies
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return {"message": "User created", "user_id": user.id}

@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    response.set_cookie(key="access_token", value=access_token, httponly=False)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    clear_token_cookies(response)
    return {"message": "Logged out"}