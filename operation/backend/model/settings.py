from datetime import timedelta
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str
    mongodb_uri: str
    access_secret_key: str
    refresh_secret_key: str

    refresh_token_expire: timedelta = timedelta(days=7)
    access_token_expire: timedelta = timedelta(minutes=15)

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        extra = "ignore"

settings = Settings()