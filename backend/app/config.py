from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Book Print API
    BOOKPRINT_API_KEY: str = ""
    BOOKPRINT_BASE_URL: str = "https://api-sandbox.sweetbook.com/v1"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./dreambook.db"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
