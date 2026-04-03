from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine, Base
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.photos import router as photos_router
from app.api.vouchers import router as vouchers_router
from app.api.books import router as books_router
from app.api.characters import router as characters_router
from app.api.orders import router as orders_router
from app.services.photo import ensure_upload_dir, UPLOAD_DIR

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
    app.include_router(photos_router, tags=["photos"])
    app.include_router(vouchers_router, tags=["vouchers"])
    app.include_router(books_router, tags=["books"])
    app.include_router(characters_router, tags=["characters"])
    app.include_router(orders_router, tags=["orders"])

    # 정적 파일 서빙 (업로드된 사진 접근용)
    ensure_upload_dir()
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

    return app


app = create_app()
