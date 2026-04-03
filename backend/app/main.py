from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 라이프사이클"""
    # startup
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown (필요 시 정리 작업)


def create_app() -> FastAPI:
    app = FastAPI(
        title="꿈꾸는 나 API",
        description="AI 직업 동화책 서비스 백엔드 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(health_router, prefix="/api", tags=["health"])
    app.include_router(auth_router, tags=["auth"])
    app.include_router(users_router, tags=["users"])

    return app


app = create_app()
