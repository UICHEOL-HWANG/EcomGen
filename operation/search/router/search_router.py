from .agent import Agent
from dto.search import SearchRequests
from fastapi import APIRouter

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},  # ✅ responses={}로 수정
)

auto_gen = Agent()

@search_router.post("/")
async def search_content(request: SearchRequests):
    query = request.query
    result = auto_gen.run(query)
    return {"query": query, "result": result}
