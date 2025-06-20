from fastapi import APIRouter, Request, HTTPException
import httpx
from typing import Optional, List
from dto.keywords import KeywordResponse, KeywordRequest
import logging
import os 

logger = logging.getLogger(__name__)

# Lambda API URL
LAMBDA_API_URL = os.getenv("LAMBDA_API_URL")

router = APIRouter(prefix="/keyword", tags=["keyword"])

@router.post("/search", response_model=Optional[List[KeywordResponse]])
async def get_keywords(request: Request, keyword_request: KeywordRequest):
    try:
        logger.info(f"Searching keywords: {keyword_request.hintKeywords}")
        
        # Lambda API 호출
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                LAMBDA_API_URL,
                json={"hintKeywords": keyword_request.hintKeywords},
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
        result = response.json()
        
        if result.get("success"):
            # Lambda 응답을 KeywordResponse 형식으로 변환
            keywords = [
                KeywordResponse(
                    relKeyword=item["relKeyword"],
                    monthlyPcQcCnt=item["monthlyPcQcCnt"]
                )
                for item in result["data"]
            ]
            
            logger.info(f"Successfully retrieved {len(keywords)} keywords")
            return keywords
        else:
            logger.error(f"Lambda API error: {result}")
            raise HTTPException(status_code=500, detail="Keyword search failed")
            
    except httpx.TimeoutException:
        logger.error("Lambda API timeout")
        raise HTTPException(status_code=408, detail="Request timeout")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Lambda API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=502, detail="External service error")
        
    except Exception as e:
        logger.error(f"Error fetching keyword data: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")