from datetime import timedelta
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str  #  데이터베이스 URL만 유지
    mongodb_uri: str  # 몽고db 연결
    access_secret_key: str  # 액세스 토큰 시크릿 키
    refresh_secret_key: str  # 리프레시 토큰 시크릿 키

    refresh_token_expire: timedelta = timedelta(days=7)
    access_token_expire: timedelta = timedelta(minutes=15)


    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"  # .env 파일에서 불러오기
        extra = "ignore" # env 안에 있던 메타데이터들 모두 무시 필요한것만 떙겨옴

settings = Settings()