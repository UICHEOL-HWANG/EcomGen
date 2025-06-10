from pydantic import BaseModel

class ProductDescriptionRequest(BaseModel):
    product_name: str

class ProductDescriptionResponse(BaseModel):
    description: str

class ProductImageRequest(BaseModel):
    product_name: str

class ProductImageResponse(BaseModel):
    image_base64: str
    message: str
