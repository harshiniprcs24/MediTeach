from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MediTeach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mediteach.db"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8081", "http://localhost:19006"]

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # AI / LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Google Vision OCR (optional)
    GOOGLE_CLOUD_CREDENTIALS: str = ""

    # Translation
    TRANSLATION_PROVIDER: str = "google"  # google | deepl | libretranslate

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
