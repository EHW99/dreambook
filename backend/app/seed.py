"""개발용 테스트 계정 + 샘플 사진 시드"""
import os
import shutil
import uuid

from PIL import Image as PILImage
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.photo import Photo
from app.services.auth import hash_password
from app.services.photo import UPLOAD_DIR, ensure_upload_dir

DEV_EMAIL = "dev@test.com"
DEV_PASSWORD = "12345678"
DEV_NAME = "체험사용자"
DEV_PHONE = "01012345678"

# samples/ 폴더 경로 (sweetbook/ 기준)
SAMPLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "samples",
)


def seed_dev_account(db: Session) -> User:
    """dev 계정이 없으면 생성, 있으면 기존 반환"""
    user = db.query(User).filter(User.email == DEV_EMAIL).first()
    if user:
        return user

    user = User(
        email=DEV_EMAIL,
        password_hash=hash_password(DEV_PASSWORD),
        name=DEV_NAME,
        phone=DEV_PHONE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[seed] 개발 계정 생성: {DEV_EMAIL}")
    return user


def seed_sample_photos(db: Session, user: User):
    """샘플 사진이 없으면 복사 + DB 등록"""
    existing = db.query(Photo).filter(Photo.user_id == user.id).count()
    if existing > 0:
        return

    if not os.path.isdir(SAMPLES_DIR):
        print(f"[seed] 샘플 폴더 없음: {SAMPLES_DIR}")
        return

    ensure_upload_dir()

    files = sorted(
        f for f in os.listdir(SAMPLES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    )

    for filename in files:
        src = os.path.join(SAMPLES_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dst = os.path.join(UPLOAD_DIR, unique_name)

        shutil.copy2(src, dst)

        try:
            img = PILImage.open(dst)
            width, height = img.size
        except Exception:
            width, height = 1024, 1024

        file_size = os.path.getsize(dst)

        photo = Photo(
            user_id=user.id,
            file_path=unique_name,
            original_name=filename,
            file_size=file_size,
            width=width,
            height=height,
        )
        db.add(photo)

    db.commit()
    print(f"[seed] 샘플 사진 {len(files)}장 등록")


def run_seed():
    """시드 실행 (서버 시작 시 호출)"""
    db = SessionLocal()
    try:
        user = seed_dev_account(db)
        seed_sample_photos(db, user)
    finally:
        db.close()
