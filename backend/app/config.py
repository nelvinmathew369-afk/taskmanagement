from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Management AI API"
    VERSION: str = "1.0.0"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/task_db"
    DB_AUTO_FALLBACK_SQLITE: bool = True

    # AI Configuration
    AI_PROVIDER: str = "auto"  # "auto", "openai", "gemini", "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # JWT Authentication
    JWT_SECRET: str = "super_secret_jwt_key_change_in_production_123456"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Check environment for API keys if not loaded from .env
if not settings.OPENAI_API_KEY and os.getenv("OPENAI_API_KEY"):
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not settings.GEMINI_API_KEY and os.getenv("GEMINI_API_KEY"):
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
