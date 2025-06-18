from pydantic import BaseModel

# Request DTO
class KeywordRequest(BaseModel):
    hintKeywords: str

# Response DTO
class KeywordResponse(BaseModel):
    relKeyword: str
    monthlyPcQcCnt: int