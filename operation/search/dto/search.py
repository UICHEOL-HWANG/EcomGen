from pydantic import BaseModel

# 요청 모델
class SearchRequests(BaseModel):
    query: str

# 응답 모델
class SearchResponse(BaseModel):
    query: str
    result: str
