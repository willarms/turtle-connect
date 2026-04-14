from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite:///./turtle.db"
    access_token_expire_minutes: int = 10080  # 7 days

    class Config:
        env_file = ".env"


settings = Settings()
