from pydantic import BaseModel

class ProductDescriptionRequest(BaseModel):
    product_name: str
    category: str
    price: int
    keywords: list[str]
    tone: str

class ProductDescriptionResponse(BaseModel):
    description: str

class ProductImageCallbackRequest(BaseModel):
    user_id: int
    product_name: str
    image_base64: str
    message: str

class CombinedProductRequest(BaseModel):
    product_name: str

class CombinedProductResponse(BaseModel):
    description: str
    image_message: str