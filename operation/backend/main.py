import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from router.auth import router as auth_router
from router.members import router as member_router
from router.generate import router as generated_router

app = FastAPI(
    title="Shop Lingo API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

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
        "X-CSRFToken"
    ],
)

app.include_router(member_router)
app.include_router(generated_router)
app.include_router(auth_router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI server is starting...\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)