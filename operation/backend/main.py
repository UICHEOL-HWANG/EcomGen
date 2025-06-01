import logging
from fastapi import FastAPI
import uvicorn
from router.auth import router as auth_router
from router.members import router as member_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(member_router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI server is starting...\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)