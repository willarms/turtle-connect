from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite:///./turtle.db"
    access_token_expire_minutes: int = 10080  # 7 days
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:5173/auth/callback"

    resend_api_key: str = ""
    email_from: str = "Turtle Connect <onboarding@resend.dev>"

    groq_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
