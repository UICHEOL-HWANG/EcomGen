from pydantic import BaseModel

class searchRequests(BaseModel):
    query : str

