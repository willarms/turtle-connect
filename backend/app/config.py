from pydantic_settings import BaseSettings
from typing import Optional



class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite:///./turtle.db"
    access_token_expire_minutes: int = 10080  # 7 days
    groq_api_key: Optional[str] = None

settings = Settings()
