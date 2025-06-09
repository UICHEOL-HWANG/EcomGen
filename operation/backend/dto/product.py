from pydantic import BaseModel

class ProductDescriptionRequest(BaseModel):
    product_name: str

class ProductDescriptionResponse(BaseModel):
    description: str
