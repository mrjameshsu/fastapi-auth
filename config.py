from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Gmail SMTP — set these in .env
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    ADMIN_EMAIL: str = "mr.jameshsu@gmail.com"
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
