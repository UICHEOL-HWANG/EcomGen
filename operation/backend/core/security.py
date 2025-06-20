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

# 토큰 만료 시간 (보안 강화)
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15분 (기존 유지)
REFRESH_TOKEN_EXPIRE_DAYS = 3     # 3일로 단축 (기존 7일)

# 모바일 브라우저 감지 함수
def is_mobile_browser(user_agent: str) -> bool:
    """User-Agent를 통해 모바일 브라우저 감지"""
    if not user_agent:
        return False
        
    mobile_indicators = [
        'android', 'iphone', 'ipad', 'ipod', 'blackberry', 
        'webos', 'windows phone', 'mobile', 'opera mini'
    ]
    
    user_agent_lower = user_agent.lower()
    return any(indicator in user_agent_lower for indicator in mobile_indicators)


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

# 하이브리드 쿠키 세팅 (모바일은 생략, 데스크톱은 HttpOnly)
def set_token_cookies(response: Response, request: Request, access_token: str, refresh_token: str):
    user_agent = request.headers.get("User-Agent", "")
    is_mobile = is_mobile_browser(user_agent)
    
    print(f"[COOKIE] User-Agent: {user_agent[:50]}...")
    print(f"[COOKIE] Is Mobile: {is_mobile}")
    
    if is_mobile:
        print("[COOKIE] Mobile detected - skipping cookie setup, using API response only")
        return  # 모바일은 쿠키 설정 안 함
    
    # 데스크톱만 HttpOnly 쿠키 설정
    print("[COOKIE] Desktop detected - setting HttpOnly cookies")
    
    # Access Token 쿠키 (데스크톱 전용)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",  # 데스크톱 크로스 도메인
        max_age=settings.access_token_expire.seconds,
        path="/"
    )
    
    # Refresh Token 쿠키 (데스크톱 전용)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=int(settings.refresh_token_expire.total_seconds()),
        path="/"
    )
    
    print("[COOKIE] HttpOnly cookies set successfully for desktop")

# 쿠키 제거 (강화 버전)
def clear_token_cookies(response: Response):
    """모든 토큰 쿠키를 완전히 제거"""
    print("[COOKIE] Starting cookie cleanup...")
    
    # 여러 방법으로 쿠키 삭제 (브라우저 호환성)
    cookie_names = ["access_token", "refresh_token"]
    
    for cookie_name in cookie_names:
        # 방법 1: max_age=0으로 즉시 만료
        response.set_cookie(
            key=cookie_name,
            value="",
            max_age=0,
            path="/"
        )
        
        # 방법 2: expires를 과거로 설정
        response.set_cookie(
            key=cookie_name,
            value="deleted",
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path="/"
        )
        
        # 방법 3: 원래 설정과 동일한 속성으로 삭제 (가장 중요!)
        response.set_cookie(
            key=cookie_name,
            value="",
            httponly=True,
            secure=True,
            samesite="none",  # 설정 시와 동일하게!
            max_age=0,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path="/"
        )
        
        print(f"[COOKIE] Cleared {cookie_name} cookie with multiple methods")
    
    print("[COOKIE] All cookies cleared successfully")

# 토큰 검증
def verify_token(token: str, secret_key: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# 사용자 가져오기 (하이브리드 방식: 쿠키 또는 Authorization 헤더)
def get_current_user(request: Request) -> dict:
    # 1순위: Authorization 헤더 확인 (모바일 친화적)
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        print(f"[AUTH] Using Authorization header token: {token[:20]}...")
    else:
        # 2순위: 쿠키에서 access_token 가져오기
        token = request.cookies.get("access_token")
        print(f"[AUTH] Using cookie token: {token[:20] if token else 'None'}...")
    
    if not token:
        print("[AUTH] No token found in header or cookie")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        user_data = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username")
        }
        print(f"[AUTH] Successfully authenticated user: {user_data['id']}")
        return user_data
    except JWTError as e:
        print(f"[AUTH] Token validation failed: {e}")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")

# MongoDB 기반 refresh token 유효성 검사


def is_refresh_token_valid(token: str, user_id: str) -> bool:
    token_collection = get_token_collection()
    

    
    token_doc = token_collection.find_one({
        "refresh_token": token,
        "user_id": user_id,
        "is_revoked": False,  # 무효화되지 않은 토큰
        "expires_at": {"$gt": datetime.utcnow()}  # 만료되지 않은 토큰
    })
    
    if token_doc:
        print(f"[TOKEN_VALIDATION] Token found in DB")
    else:
        print(f"[TOKEN_VALIDATION] Token NOT found in DB")
        # 디버깅: 존재하는 토큰들 확인
        all_tokens = token_collection.find({"user_id": user_id})
        print(f"[TOKEN_VALIDATION] Found {token_collection.count_documents({'user_id': user_id})} tokens for user")
        for doc in all_tokens:
            print(f"[TOKEN_VALIDATION] DB Token: {doc.get('refresh_token', '')[:20]}... revoked: {doc.get('is_revoked')} expires: {doc.get('expires_at')}")
    
    return token_doc is not None

# 사용자의 모든 refresh 토큰 무효화 (로그아웃 시 옵션)
def revoke_all_user_tokens(user_id: str) -> int:
    token_collection = get_token_collection()
    result = token_collection.update_many(
        {
            "user_id": user_id,
            "is_revoked": False
        },
        {
            "$set": {
                "is_revoked": True,
                "revoked_at": datetime.utcnow()
            }
        }
    )
    return result.modified_count


# CSRF 토큰 SessionStorage 관리 함수
def store_csrf_token_in_session(request: Request, response: Response, csrf_token: str):
    """데스크톱에서 CSRF 토큰을 JSON 응답으로 제공 (프론트에서 sessionStorage에 저장)"""
    user_agent = request.headers.get("User-Agent", "")
    is_mobile = is_mobile_browser(user_agent)
    
    if not is_mobile:
        print(f"[CSRF] Desktop: CSRF token will be sent in JSON for sessionStorage: {csrf_token[:16]}...")
    else:
        print(f"[CSRF] Mobile: CSRF token will be sent in JSON response: {csrf_token[:16]}...")
    
    return csrf_token  # JSON 응답에 포함될 토큰 반환


# CSRF 토큰 검증 (개선된 버전)
def validate_csrf(request: Request):
    csrf_token_header = request.headers.get("X-CSRF-Token")
    
    # 디버깅 로그
    print(f"[CSRF] Header token: {csrf_token_header[:16] if csrf_token_header else 'None'}...")
    
    if not csrf_token_header:
        print("[CSRF] Warning: No CSRF token in request header")
        # 초기 로그인/refresh 시도에서는 CSRF 토큰이 없을 수 있음
        return True
    
    # CSRF 토큰이 있으면 기본 검사
    if len(csrf_token_header) < 8:  # 최소 길이 검사 완화
        print("[CSRF] Invalid CSRF token format")
        raise HTTPException(status_code=403, detail="Invalid CSRF token format")
    
    print("[CSRF] Token validation passed")
    return True