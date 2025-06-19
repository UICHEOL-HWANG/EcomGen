from fastapi import APIRouter, Request
from service.keyword_service import getresults
from typing import Optional, List
from dto.keywords import KeywordResponse, KeywordRequest
import json

router = APIRouter(prefix="/keyword", tags=["keyword"])

@router.post("/search", response_model=Optional[List[KeywordResponse]])
async def get_keywords(request: Request, keyword_request: KeywordRequest):
    try:
        # 요청 데이터 로깅
        body = await request.body()
        print(f"Raw request body: {body.decode('utf-8')}")
        print(f"Parsed request: {keyword_request}")
        print(f"hintKeywords: '{keyword_request.hintKeywords}'")
        print(f"hintKeywords type: {type(keyword_request.hintKeywords)}")
        
        keyword = getresults(keyword_request.hintKeywords)
        print(f"Keyword service result: {keyword}")
        return keyword
    except Exception as e:
        print(f"Error fetching keyword data: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None
