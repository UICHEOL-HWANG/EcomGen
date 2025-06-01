from datetime import datetime
from pydantic import BaseModel

class TokenData(BaseModel):
    sub: str
    email: str
    username: str
    exp: datetime