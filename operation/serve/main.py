
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from router.generate_router import generate_router
from router.generate_model import create_async_llm_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
)

@app.on_event("startup")
async def startup_event():
    app.state.llm = create_async_llm_engine("UICHEOL-HWANG/EcomGen-0.0.1v")

app.include_router(generate_router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

