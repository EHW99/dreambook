"""캐릭터 시트 서비스 레이어"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.character_sheet import CharacterSheet


# 최대 재생성 횟수 (최초 1회 + 재생성 4회 = 총 5회)
MAX_CHARACTER_GENERATIONS = 5


def create_character_sheet(db: Session, book: Book) -> CharacterSheet:
    """캐릭터 시트 생성 (Phase 2: 더미 이미지)"""
    # 현재 생성된 캐릭터 수 확인
    existing_count = db.query(CharacterSheet).filter(
        CharacterSheet.book_id == book.id
    ).count()

    if existing_count >= MAX_CHARACTER_GENERATIONS:
        raise ValueError("재생성 횟수를 모두 사용했습니다")

    # 더미 이미지 경로 (Phase 2)
    dummy_image_path = f"/uploads/characters/dummy_character_{existing_count}.png"

    character = CharacterSheet(
        book_id=book.id,
        image_path=dummy_image_path,
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
