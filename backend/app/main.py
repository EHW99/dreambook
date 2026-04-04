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
from app.api.webhooks import router as webhooks_router
from app.api.aptitude import router as aptitude_router
from app.services.photo import ensure_upload_dir, UPLOAD_DIR

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 라이프사이클"""
    # startup
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # 기존 DB에 새 컬럼이 없으면 추가 (SQLite ALTER TABLE)
    from sqlalchemy import inspect, text
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            existing_cols = {c["name"] for c in inspector.get_columns("users")}
            if "name" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''"))
            if "phone" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT ''"))
            conn.commit()

    # 개발용 테스트 계정 시드
    from app.seed import run_seed
    run_seed()

    # Book Print API 판형 로드
    from app.services.bookprint import load_book_specs
    await load_book_specs()

    # 웹훅 자동 등록 (WEBHOOK_URL 설정 시)
    if settings.WEBHOOK_URL and settings.BOOKPRINT_API_KEY:
        import logging
        logger = logging.getLogger(__name__)
        try:
            from app.services.bookprint import BookPrintService
            service = BookPrintService()
            result = await service.register_webhook(settings.WEBHOOK_URL)
            secret_key = result.get("data", {}).get("secretKey", "")
            if secret_key:
                # 최초 등록 시 secretKey를 WEBHOOK_SECRET에 반영
                from app.api import webhooks
                webhooks.WEBHOOK_SECRET = secret_key
                logger.info(f"웹훅 등록 완료: {settings.WEBHOOK_URL}")
            else:
                logger.info("웹훅 설정 확인 완료 (기존 등록)")
            await service.close()
        except Exception as e:
            logger.warning(f"웹훅 자동 등록 실패 (서비스 시작에 영향 없음): {e}")

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
    app.include_router(webhooks_router, tags=["webhooks"])
    app.include_router(aptitude_router, tags=["aptitude"])

    # 정적 파일 서빙 (업로드된 사진 접근용)
    ensure_upload_dir()
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

    return app


app = create_app()
