from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Modules
from search.agent.search_router import search_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
)

app.include_router(search_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8196, reload=True)
