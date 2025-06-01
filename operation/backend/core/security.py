from model.settings import settings
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.responses import Response
from jose import JWTError, jwt
from dto.token import TokenData
from starlette.status import HTTP_401_UNAUTHORIZED

from utils.pymongo import get_token_collection


# 환경 변수
ACCESS_SECRET_KEY = settings.access_secret_key
REFRESH_SECRET_KEY = settings.refresh_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


# JWT 생성
def create_access_token(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "email": email,
        "username": username
    }
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

# 쿠키 세팅
def set_token_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: Optional[str] = None):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.access_token_expire.seconds
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.refresh_token_expire.total_seconds()
    )
    if csrf_token:
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=settings.access_token_expire.seconds
        )

# 쿠키 제거
def clear_token_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

# 토큰 검증
def verify_token(token: str, secret_key: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# 사용자 가져오기 (FastAPI 의존성으로)
def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username")
        }
    except JWTError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")

# MongoDB 기반 refresh token 유효성 검사


def is_refresh_token_valid(token: str, user_id: str) -> bool:
    token_collection = get_token_collection()
    token_doc = token_collection.find_one({
        "refresh_token": token,
        "user_id": user_id,
        "is_revoked": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    return token_doc is not None


# CSRF 토큰 검증
def validate_csrf(request: Request):
    csrf_cookie = request.cookies.get("csrf_token", "")
    csrf_header = request.headers.get("X-CSRF-Token", "")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")