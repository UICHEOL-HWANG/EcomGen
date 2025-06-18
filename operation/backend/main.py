import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from router.auth import router as auth_router
from router.members import router as member_router
from router.generate import router as generated_router
from router.product_search import router as product_search_router
from router.report import router as report_router

app = FastAPI(
    title="Shop Lingo API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 보안 헤더 미들웨어 추가
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    # 기본 보안 헤더
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # 경로에 따라 CSP 다르게 설정
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi.json"):
        # Swagger UI용 CSP
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https://lingoapi.store;"
        )
    else:
        # 일반 요청용 CSP (보안 강화)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "font-src 'self'; "
            "connect-src 'self';"
        )

    return response

# CORS 설정 - withCredentials: true를 위해 구체적인 origin 지정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://shop-lingo.store"
    ],
    allow_credentials=True,  # 쿠키 전송 허용
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "X-CSRF-Token", 
        "X-CSRFToken",
        "X-Refresh-Token"  # 모바일용 추가
    ],
)

app.include_router(member_router)
app.include_router(generated_router)
app.include_router(auth_router)
app.include_router(product_search_router)
app.include_router(report_router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI server is starting...\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)