from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Book Print API
    BOOKPRINT_API_KEY: str = ""
    BOOKPRINT_BASE_URL: str = "https://api-sandbox.sweetbook.com/v1"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # ── AI 모델 설정 ──
    # 텍스트 모델: 스토리 생성, 줄거리 생성, 직업 번역에 사용
    # 선택지: gpt-4o, gpt-4o-mini
    TEXT_MODEL: str = "gpt-4o-mini"

    # 이미지 모델: 캐릭터 시트, 일러스트, 표지 생성에 사용
    # 선택지: gpt-image-1, gpt-image-1-mini, gpt-image-1.5
    IMAGE_MODEL: str = "gpt-image-1.5"

    # 이미지 품질: low / medium / high
    IMAGE_QUALITY: str = "low"

    # JWT (반드시 .env에서 설정할 것)
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./dreambook.db"

    # Webhook
    WEBHOOK_SECRET: str = ""
    WEBHOOK_URL: str = ""  # 웹훅 수신 URL (서버 시작 시 등록에 사용)

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
