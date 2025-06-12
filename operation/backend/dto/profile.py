from pydantic import BaseModel

class ProfileUploadRequest(BaseModel):
    user_id: str
    base64_data: str