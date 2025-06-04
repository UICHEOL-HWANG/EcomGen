# pip Modules
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
import secrets
from jose import JWTError, jwt
from datetime import datetime

# My Modules
from dto.user import UserCreate, UserLogin
from model.database import get_db
from model.settings import settings
from service.auth_service import create_user, authenticate_user
from core.security import (
    create_access_token, create_refresh_token,
    set_token_cookies, clear_token_cookies, validate_csrf,
    is_refresh_token_valid
)
from utils.pymongo import get_token_collection


router = APIRouter(prefix="/auth", tags=["auth"])

token_collection = get_token_collection()

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return {"message": "User created", "user_id": user.id}

@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )
    refresh_token = create_refresh_token(str(user.id))
    csrf_token = secrets.token_hex(16)

    # Save refresh_token to MongoDB
    token_collection.insert_one({
        "user_id": str(user.id),
        "refresh_token": refresh_token,
        "expires_at": datetime.utcnow() + settings.refresh_token_expire,
        "is_revoked": False,
        "created_at": datetime.utcnow()
    })

    set_token_cookies(response, access_token, refresh_token, csrf_token)

    return {
        "message": "Login successful",
    }

@router.post("/logout")
def logout(request: Request, response: Response):
    validate_csrf(request)
    refresh_token = request.cookies.get("refresh_token")
    user_id = None

    try:
        payload = jwt.decode(
            refresh_token,
            key=settings.refresh_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except JWTError:
        pass

    if refresh_token and user_id:
        token_collection.insert_one({
            "token": refresh_token,
            "user_id": user_id,
            "blacklisted_at": datetime.utcnow()
        })

    clear_token_cookies(response)
    response.delete_cookie("csrf_token")
    return {"message": "Logged out"}

@router.post("/refresh")
def refresh_token(request: Request, response: Response):
    validate_csrf(request)
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(
            refresh_token,
            key=settings.refresh_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if not is_refresh_token_valid(refresh_token, user_id):
        raise HTTPException(status_code=401, detail="Refresh token is invalid or revoked")

    new_access_token = create_access_token(user_id)
    csrf_token = request.cookies.get("csrf_token") or secrets.token_hex(16)

    set_token_cookies(response, new_access_token, refresh_token, csrf_token)
    return {"message": "Access token refreshed"}