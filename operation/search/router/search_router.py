from .search import search_data
from dto.search import SearchRequests
from fastapi import APIRouter

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},  # ✅ responses={}로 수정
)


