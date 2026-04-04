"""캐릭터 시트 서비스 레이어

Phase 3: OPENAI_API_KEY가 설정되어 있으면 GPT Image로 캐릭터 시트 생성.
폴백: API 키가 없거나 photo_id가 없으면 더미 이미지 사용.
"""
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.book import Book
from app.models.character_sheet import CharacterSheet
from app.models.photo import Photo
from app.services.photo import UPLOAD_DIR

logger = logging.getLogger(__name__)


# 최대 재생성 횟수 (최초 1회 + 재생성 4회 = 총 5회)
MAX_CHARACTER_GENERATIONS = 5

# 캐릭터 시트 저장 디렉토리
CHARACTER_DIR = os.path.join(UPLOAD_DIR, "characters")


def _ensure_character_dir():
    """캐릭터 시트 저장 디렉토리가 존재하도록 보장"""
    os.makedirs(CHARACTER_DIR, exist_ok=True)


def _generate_ai_character(db: Session, book: Book) -> Optional[str]:
    """GPT Image로 캐릭터 시트를 생성하고 파일 경로를 반환한다.

    AI 생성이 불가능한 경우 None을 반환한다.
    """
    settings = get_settings()

    # API 키가 없으면 AI 생성 불가
    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 캐릭터 폴백")
        return None

    # 아이 사진이 없으면 AI 생성 불가
    if not book.photo_id:
        logger.info("photo_id 미설정 — 더미 캐릭터 폴백")
        return None

    # 사진 파일 경로 조회
    photo = db.query(Photo).filter(Photo.id == book.photo_id).first()
    if not photo or not os.path.exists(photo.file_path):
        logger.warning(f"사진 파일을 찾을 수 없음: photo_id={book.photo_id}")
        return None

    # 그림체 및 직업 정보
    art_style = book.art_style or "watercolor"
    job_name = book.job_name or "소방관"
    story_style = book.story_style or "dreaming_today"

    try:
        from app.services.ai_character import generate_character_image, CharacterGenerationError

        image_bytes = generate_character_image(
            photo_path=photo.file_path,
            art_style=art_style,
            job_name=job_name,
            story_style=story_style,
        )

        # 파일 저장
        _ensure_character_dir()
        filename = f"character_{book.id}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(CHARACTER_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        logger.info(f"AI 캐릭터 시트 생성 완료: {filepath}")
        # /uploads/characters/filename.png 형태의 URL 경로 반환
        return f"/uploads/characters/{filename}"

    except CharacterGenerationError:
        raise  # 콘텐츠 정책 위반 등은 상위로 전파
    except Exception as e:
        logger.error(f"AI 캐릭터 생성 실패, 더미 폴백: {e}")
        return None


def create_character_sheet(db: Session, book: Book) -> CharacterSheet:
    """캐릭터 시트 생성 (AI 또는 더미)"""
    # 현재 생성된 캐릭터 수 확인
    existing_count = db.query(CharacterSheet).filter(
        CharacterSheet.book_id == book.id
    ).count()

    if existing_count >= MAX_CHARACTER_GENERATIONS:
        raise ValueError("재생성 횟수를 모두 사용했습니다")

    # AI 캐릭터 생성 시도
    image_path = _generate_ai_character(db, book)

    # AI 생성 실패 시 더미 이미지 경로
    if image_path is None:
        image_path = f"/uploads/characters/dummy_character_{existing_count}.png"

    character = CharacterSheet(
        book_id=book.id,
        image_path=image_path,
        generation_index=existing_count,
        is_selected=False,
    )
    db.add(character)

    # 재생성 횟수 업데이트 (첫 번째 생성은 카운트하지 않음)
    if existing_count > 0:
        book.character_regen_count = existing_count
        book.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(character)
    return character


def get_character_sheets(db: Session, book_id: int) -> List[CharacterSheet]:
    """캐릭터 시트 갤러리 조회"""
    return db.query(CharacterSheet).filter(
        CharacterSheet.book_id == book_id
    ).order_by(CharacterSheet.generation_index).all()


def get_character_sheet_by_id(db: Session, char_id: int) -> Optional[CharacterSheet]:
    """캐릭터 시트 ID로 조회"""
    return db.query(CharacterSheet).filter(CharacterSheet.id == char_id).first()


def select_character_sheet(db: Session, book_id: int, char_id: int) -> Optional[CharacterSheet]:
    """캐릭터 시트 선택 (기존 선택 해제 후 선택, book.status를 character_confirmed로 전이)"""
    character = db.query(CharacterSheet).filter(
        CharacterSheet.id == char_id,
        CharacterSheet.book_id == book_id,
    ).first()

    if not character:
        return None

    # 기존 선택 해제
    db.query(CharacterSheet).filter(
        CharacterSheet.book_id == book_id,
        CharacterSheet.is_selected == True,
    ).update({"is_selected": False})

    # 새로 선택
    character.is_selected = True

    # book.status를 character_confirmed로 전이
    book = db.query(Book).filter(Book.id == book_id).first()
    if book and book.status == "draft":
        book.status = "character_confirmed"
        book.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(character)
    return character
