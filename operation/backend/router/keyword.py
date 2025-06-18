from fastapi import APIRouter
from service.keyword_service import getresults
from typing import Optional, List
from dto.keywords import KeywordResponse, KeywordRequest

router = APIRouter(prefix="/keyword", tags=["keyword"])

@router.post("/search", response_model=Optional[List[KeywordResponse]])
def get_keywords(request: KeywordRequest):

    try:
        keyword = getresults(request.hintKeywords)
        return keyword
    except Exception as e:
        print(f"Error fetching keyword data: {e}")
        return None
