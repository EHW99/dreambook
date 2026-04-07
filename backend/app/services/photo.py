"""사진 서비스 — 업로드, 목록 조회, 삭제"""
import os
import uuid
from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from app.models.photo import Photo

# 허용 확장자 → MIME Content-Type 매핑
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_RESOLUTION = 512
MAX_PHOTOS_PER_USER = 20

# 업로드 디렉토리 (backend/ 기준)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def ensure_upload_dir():
    """uploads 디렉토리가 없으면 생성"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_photo_count(db: Session, user_id: int) -> int:
    return db.query(Photo).filter(Photo.user_id == user_id).count()


def get_photos_by_user(db: Session, user_id: int) -> list[Photo]:
    return (
        db.query(Photo)
        .filter(Photo.user_id == user_id)
        .order_by(Photo.created_at.desc())
        .all()
    )


def get_photo_by_id(db: Session, photo_id: int) -> Photo | None:
    return db.query(Photo).filter(Photo.id == photo_id).first()


def validate_file_extension(filename: str) -> bool:
    """파일 확장자가 허용 형식인지 확인"""
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_content_type(content_type: str) -> bool:
    """Content-Type이 허용 형식인지 확인"""
    return content_type in ALLOWED_CONTENT_TYPES


def validate_file_size(file_data: bytes) -> bool:
    """파일 크기가 10MB 이하인지 확인"""
    return len(file_data) <= MAX_FILE_SIZE


def validate_resolution(file_data: bytes) -> tuple[bool, int, int]:
    """이미지 해상도를 읽어 반환. 제한 없음."""
    try:
        img = Image.open(BytesIO(file_data))
        width, height = img.size
        return True, width, height
    except Exception:
        return False, 0, 0


def save_photo_file(file_data: bytes, original_name: str) -> str:
    """파일을 uploads/ 디렉토리에 UUID 이름으로 저장하고, 상대 경로를 반환"""
    ensure_upload_dir()
    ext = os.path.splitext(original_name)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_data)
    return unique_name


def create_photo(
    db: Session,
    user_id: int,
    file_name: str,
    original_name: str,
    file_size: int,
    width: int,
    height: int,
) -> Photo:
    """DB에 사진 레코드 생성"""
    photo = Photo(
        user_id=user_id,
        file_path=file_name,
        original_name=original_name,
        file_size=file_size,
        width=width,
        height=height,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo: Photo):
    """DB 레코드 + 서버 파일 삭제"""
    # 파일 삭제
    file_path = os.path.join(UPLOAD_DIR, photo.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(photo)
    db.commit()
