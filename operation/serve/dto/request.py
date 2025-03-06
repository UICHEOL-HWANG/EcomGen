from pydantic import BaseModel

class GenerateRequest(BaseModel):
    product_name : str