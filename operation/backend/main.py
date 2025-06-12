import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from router.auth import router as auth_router
from router.members import router as member_router
from router.generate import router as generated_router
import mangum


app = FastAPI(
    title="Shop Lingo API",
    root_path="/v1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시에는 origin 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(member_router)
app.include_router(generated_router)
app.include_router(auth_router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI server is starting...\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)