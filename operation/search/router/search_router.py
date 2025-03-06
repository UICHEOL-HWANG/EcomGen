from .search import search_data
from dto.search import SearchRequests
from fastapi import APIRouter

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},  # ✅ responses={}로 수정
)

@search_router.post("/", response_model=SearchRequests)  # ✅ DTO 클래스 이름 수정
async def search(search_request: SearchRequests):  # ✅ DTO 클래스 이름 수정
    return search_data(search_request)
