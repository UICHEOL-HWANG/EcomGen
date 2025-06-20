from pydantic import BaseModel, validator

# Request DTO
class KeywordRequest(BaseModel):
    hintKeywords: str
    
    @validator('hintKeywords')
    def validate_hint_keywords(cls, v):
        if not v or not v.strip():
            raise ValueError('hintKeywords cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "hintKeywords": "신발"
            }
        }

# Response DTO
class KeywordResponse(BaseModel):
    relKeyword: str
    monthlyPcQcCnt: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "relKeyword": "나이키 신발",
                "monthlyPcQcCnt": 125000
            }
        }