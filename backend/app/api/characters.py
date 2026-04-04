"""캐릭터 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.character import CharacterSheetResponse
from app.services.book import get_book_by_id
from app.services.ai_character import CharacterGenerationError
from app.services.character import (
    create_character_sheet,
    get_character_sheets,
    select_character_sheet,
)

router = APIRouter(prefix="/api/books")


def _get_user_book(db: Session, book_id: int, user: User):
    """책 조회 + 소유권 확인 헬퍼"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 접근할 수 있습니다",
        )
    return book


@router.post(
    "/{book_id}/character",
    response_model=CharacterSheetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_character(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """캐릭터 시트 생성 (AI 생성, API 키 없으면 더미 폴백)"""
    book = _get_user_book(db, book_id, user)

    try:
        character = create_character_sheet(db, book)
    except CharacterGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    return character


@router.get(
    "/{book_id}/characters",
    response_model=List[CharacterSheetResponse],
)
def list_characters(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """캐릭터 시트 갤러리 조회"""
    _get_user_book(db, book_id, user)
    characters = get_character_sheets(db, book_id)
    return characters


@router.patch(
    "/{book_id}/character/{char_id}/select",
    response_model=CharacterSheetResponse,
)
def select_character(
    book_id: int,
    char_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """캐릭터 시트 선택 (확정)"""
    _get_user_book(db, book_id, user)

    character = select_character_sheet(db, book_id, char_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캐릭터 시트를 찾을 수 없습니다",
        )

    return character
