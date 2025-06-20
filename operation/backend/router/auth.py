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
    is_refresh_token_valid, store_csrf_token_in_session
)
from utils.pymongo import get_token_collection
from model.models import Member 


router = APIRouter(prefix="/auth", tags=["auth"])

token_collection = get_token_collection()

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return {"message": "User created", "user_id": user.id}

@router.post("/login")
def login(user_data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(Member).filter_by(email=user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="없는 유저 입니다.")

    if not authenticate_user(db, user_data.email, user_data.password):
        raise HTTPException(status_code=400, detail="비밀번호 검증 실패")

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )
    refresh_token = create_refresh_token(str(user.id))
    csrf_token = secrets.token_hex(16)
    
    print(f"[LOGIN] User {user.id} logging in")
    print(f"[LOGIN] Generated refresh token: {refresh_token[:20]}...")

    # Save refresh_token to MongoDB
    token_doc = {
        "user_id": str(user.id),
        "refresh_token": refresh_token,
        "expires_at": datetime.utcnow() + settings.refresh_token_expire,
        "is_revoked": False,
        "created_at": datetime.utcnow()
    }
    
    result = token_collection.insert_one(token_doc)
    print(f"[LOGIN] Token saved to MongoDB: {result.inserted_id}")

    # 모바일/데스크톱 구분 응답
    user_agent = request.headers.get("User-Agent", "")
    is_mobile = "mobile" in user_agent.lower() or "android" in user_agent.lower() or "iphone" in user_agent.lower()
    
    if is_mobile:
        # 모바일: JSON에 토큰 포함
        return {
            "message": "Login successful",
            "csrf_token": csrf_token,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    else:
        # 데스크톱: 쿠키에 access/refresh, JSON에 CSRF 토큰 (프론트에서 sessionStorage에 저장)
        
        # 1. 쿠키에 access/refresh 토큰 저장
        set_token_cookies(response, request, access_token, refresh_token)
        
        # 2. CSRF 토큰 처리 (프론트에서 sessionStorage에 저장하도록)
        store_csrf_token_in_session(request, response, csrf_token)
        
        # 3. JSON 응답에 CSRF 토큰 포함 (프론트에서 sessionStorage에 저장)
        return {
            "message": "Login successful",
            "csrf_token": csrf_token
        }

@router.post("/logout")
def logout(request: Request, response: Response):
    validate_csrf(request)
    
    # 쿠키와 헤더에서 토큰 가져오기
    refresh_token = request.cookies.get("refresh_token")
    access_token = None
    user_id = None
    
    # Access 토큰 가져오기 (쿠키 또는 헤더에서)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
    else:
        access_token = request.cookies.get("access_token")
    
    # Refresh 토큰에서 user_id 추출
    try:
        payload = jwt.decode(
            refresh_token,
            key=settings.refresh_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
    except JWTError:
        pass

    # 1. Refresh 토큰 무효화 (MongoDB)
    if refresh_token and user_id:
        token_collection.update_one(
            {
                "refresh_token": refresh_token,
                "user_id": user_id
            },
            {
                "$set": {
                    "is_revoked": True,
                    "revoked_at": datetime.utcnow()
                }
            }
        )
        print(f"[LOGOUT] Revoked refresh token for user {user_id}")
    
    # 2. Access 토큰 블랙리스트 등록 (MongoDB)
    if access_token and user_id:
        try:
            # Access 토큰 디코딩해서 만료 시간 확인
            access_payload = jwt.decode(
                access_token,
                key=settings.access_secret_key,
                algorithms=["HS256"]
            )
            access_exp = datetime.utcfromtimestamp(access_payload.get("exp"))
            
            # 블랙리스트에 등록
            blacklist_doc = {
                "token_type": "access",
                "token": access_token,
                "user_id": user_id,
                "blacklisted_at": datetime.utcnow(),
                "expires_at": access_exp  # 토큰 만료 시간까지만 블랙리스트 유지
            }
            token_collection.insert_one(blacklist_doc)
            print(f"[LOGOUT] Blacklisted access token for user {user_id}")
            
        except JWTError as e:
            print(f"[LOGOUT] Failed to decode access token: {e}")

    # 모바일/데스크톱 구분 응답
    user_agent = request.headers.get("User-Agent", "")
    is_mobile = "mobile" in user_agent.lower() or "android" in user_agent.lower() or "iphone" in user_agent.lower()
    
    if is_mobile:
        # 모바일: 쿠키 제거 + JSON 응답에 클리어 지시
        clear_token_cookies(response)
        return {
            "message": "Logged out",
            "clear_tokens": True,  # 모바일 앱에서 토큰 삭제 지시
            "clear_csrf": True     # CSRF 토큰 삭제 지시
        }
    else:
        # 데스크톱: 쿠키 제거 + JSON 응답에 CSRF 삭제 지시
        clear_token_cookies(response)
        return {
            "message": "Logged out",
            "clear_csrf": True  # 프론트에서 sessionStorage.removeItem('csrf_token') 실행
        }

@router.post("/refresh")
def refresh_token(request: Request, response: Response):
    validate_csrf(request)
    
    # 하이브리드 방식: 쿠키 또는 Authorization 헤더에서 refresh 토큰 가져오기
    refresh_token = None
    
    # 1순위: Authorization 헤더 확인
    auth_header = request.headers.get("X-Refresh-Token")
    if auth_header:
        refresh_token = auth_header
        print(f"[REFRESH] Using X-Refresh-Token header: {refresh_token[:20]}...")
    else:
        # 2순위: 쿠키에서 가져오기
        refresh_token = request.cookies.get("refresh_token")
        print(f"[REFRESH] Using cookie refresh token: {refresh_token[:20] if refresh_token else 'None'}...")
    
    if not refresh_token:
        print("[REFRESH] No refresh token found in header or cookie")
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(
            refresh_token,
            key=settings.refresh_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        print(f"[REFRESH] Decoded user_id: {user_id}")
        
        if user_id is None:
            print("[REFRESH] No user_id in token payload")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError as e:
        print(f"[REFRESH] JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # 토큰 유효성 검사
    is_valid = is_refresh_token_valid(refresh_token, user_id)
    print(f"[REFRESH] Token validation result: {is_valid}")
    
    if not is_valid:
        print(f"[REFRESH] Token validation failed for user {user_id}")
        raise HTTPException(status_code=401, detail="Refresh token is invalid or revoked")

    new_access_token = create_access_token(user_id)
    new_csrf_token = secrets.token_hex(16)  # 새로운 CSRF 토큰 생성
    
    print(f"[REFRESH] New tokens generated for user {user_id}")
    print(f"[REFRESH] New CSRF token: {new_csrf_token[:16]}...")

    # 모바일/데스크톱 구분 응답
    user_agent = request.headers.get("User-Agent", "")
    is_mobile = "mobile" in user_agent.lower() or "android" in user_agent.lower() or "iphone" in user_agent.lower()
    
    if is_mobile:
        # 모바일: JSON에 모든 토큰 포함
        return {
            "message": "Access token refreshed",
            "access_token": new_access_token,
            "refresh_token": refresh_token,  # 기존 refresh 토큰 유지
            "csrf_token": new_csrf_token
        }
    else:
        # 데스크톱: 쿠키에 access 토큰 업데이트, JSON에 CSRF 토큰
        
        # 1. 쿠키에 access/refresh 토큰 업데이트
        set_token_cookies(response, request, new_access_token, refresh_token)
        
        # 2. CSRF 토큰 처리
        store_csrf_token_in_session(request, response, new_csrf_token)
        
        # 3. JSON 응답에 CSRF 토큰 포함 (프론트에서 sessionStorage에 업데이트)
        return {
            "message": "Access token refreshed",
            "csrf_token": new_csrf_token
        }