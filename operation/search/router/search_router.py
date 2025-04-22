from operation.search.agent.initialized_model import Agent
from dto.search import SearchResponse, SearchRequests
from agent.
from fastapi import APIRouter

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},  # ✅ responses={}로 수정
)

auto_gen = Agent()

@search_router.post("/", response_model=SearchResponse)
async def search_content(request: SearchRequests):
    query = request.query
    result = auto_gen(query)
    return SearchResponse(query=query, result=result)
