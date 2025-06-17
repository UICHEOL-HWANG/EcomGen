from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductDescriptionRequest(BaseModel):
    product_name: str
    category: str
    price: int
    keywords: List[str]
    tone: str

class ProductDescriptionResponse(BaseModel):
    description: str

class ProductImageCallbackRequest(BaseModel):
    job_id: str  # 추가
    user_id: int
    product_name_ko: str  # 수정: product_name -> product_name_ko
    product_name_en: str  # 추가
    prompt: str  # 추가
    image_base64: str

class CombinedProductRequest(BaseModel):
    product_name: str
    category: str
    price: int
    keywords: List[str]
    tone: str

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "여름용 반팔 셔츠",
                "category": "상의",
                "price": 19900,
                "keywords": ["여름", "쿨링", "화이트"],
                "tone": "친근한"
            }
        }

class CombinedProductResponse(BaseModel):
    job_id: str  # 추가: 작업 추적용 ID
    description: str
    image_message: str

# 텍스트 콜백용 DTO 추가
class ProductTextCallbackRequest(BaseModel):
    job_id: str
    user_id: int
    product_name: str
    description: str
    prompt: str
    category: Optional[str] = None
    price: Optional[int] = None
    keywords: Optional[List[str]] = None
    tone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "12345678-1234-1234-1234-123456789012",
                "user_id": 1,
                "product_name": "여름용 반팔 셔츠",
                "description": "이 여름용 반팔 셔츠는 통기성이 뛰어난 면 소재로 제작되어...",
                "prompt": "Generate a product description for summer t-shirt...",
                "category": "상의",
                "price": 19900,
                "keywords": ["여름", "쿨링", "화이트"],
                "tone": "친근한"
            }
        }

class ProductTextCallbackResponse(BaseModel):
    message: str

# 작업 상태 확인용 DTO 추가
class GenerationStatusResponse(BaseModel):
    job_id: str
    text_completed: bool
    image_completed: bool
    text_data: Optional[dict] = None
    image_data: Optional[dict] = None
    completed: bool

# 사용자 생성 상품 조회용 DTO 추가
class UserProductResponse(BaseModel):
    id: int
    job_id: Optional[str]
    product_name: str
    username: Optional[str] = None
    description: str
    category: Optional[str]
    price: Optional[int]
    keywords: List[str]
    tone: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProductsListResponse(BaseModel):
    products: List[UserProductResponse]
    total: int
    categories: List[str]

class ProductDeleteResponse(BaseModel):
    message: str
    deleted_product_id: int