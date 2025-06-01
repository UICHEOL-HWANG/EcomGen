import logging
from fastapi import FastAPI
import uvicorn
from router.auth import router

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI server is starting...\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)