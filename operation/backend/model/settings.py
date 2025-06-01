from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str  #  데이터베이스 URL만 유지

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"  # .env 파일에서 불러오기
        extra = "ignore" # env 안에 있던 메타데이터들 모두 무시 필요한것만 떙겨옴

settings = Settings()