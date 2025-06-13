from pydantic import BaseModel

class CombinedProductRequest(BaseModel):
    product_name: str

class CombinedProductResponse(BaseModel):
    description: str
    image_message: str
