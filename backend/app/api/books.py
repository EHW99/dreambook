"""동화책 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.page import Page
from app.schemas.book import (
    BookCreateRequest, BookUpdateRequest, BookResponse, BookListResponse,
    GenerateResponse, PageResponse,
)
from app.services.book import create_book, get_book_by_id, get_books_by_user, update_book, delete_book
from app.services.generate import generate_dummy_story
from app.services.voucher import get_voucher_by_id, use_voucher

router = APIRouter(prefix="/api/books")


@router.get("", response_model=List[BookListResponse])
def list_books(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 동화책 목록 조회"""
    books = get_books_by_user(db, user.id)
    return books


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create(
    req: BookCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 생성 (이용권 연결)"""
    # 이용권 확인
    voucher = get_voucher_by_id(db, req.voucher_id)
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이용권을 찾을 수 없습니다",
        )
    if voucher.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 이용권만 사용할 수 있습니다",
        )
    if voucher.status != "purchased":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용된 이용권입니다",
        )

    # 동화책 생성
    book = create_book(db, user.id, voucher.id)

    # 이용권 사용 처리
    use_voucher(db, voucher, book.id)

    # book 새로고침 (voucher 연결 후)
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 상세 조회"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 조회할 수 있습니다",
        )
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update(
    book_id: int,
    req: BookUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 정보 수정 (단계별 저장)"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 수정할 수 있습니다",
        )

    # photo_id 유효성 검사
    if req.photo_id is not None:
        from app.models.photo import Photo
        photo = db.query(Photo).filter(Photo.id == req.photo_id, Photo.user_id == user.id).first()
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사진을 찾을 수 없습니다",
            )

    # step 5→6 전환 시 캐릭터 선택 여부 서버 측 검증
    if req.current_step is not None and req.current_step >= 6 and book.current_step <= 5:
        from app.models.character_sheet import CharacterSheet
        selected = db.query(CharacterSheet).filter(
            CharacterSheet.book_id == book.id,
            CharacterSheet.is_selected == True,
        ).first()
        if not selected:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="캐릭터를 선택해주세요",
            )

    update_data = req.model_dump(exclude_unset=True)
    book = update_book(db, book, **update_data)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
def delete(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 삭제 (draft 상태만)"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 삭제할 수 있습니다",
        )
    if book.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="작성 중인 동화책만 삭제할 수 있습니다",
        )
    delete_book(db, book)
    return {"message": "동화책이 삭제되었습니다"}


@router.post("/{book_id}/generate", response_model=GenerateResponse)
def generate(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """더미 스토리+이미지 생성 (Phase 2)"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 생성할 수 있습니다",
        )

    # 이미 생성된 동화책은 재생성 방어
    if book.status not in ("draft", "character_confirmed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미 생성된 동화책입니다",
        )

    # 필수 정보 검증
    if not book.child_name or book.child_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="아이 이름이 입력되지 않았습니다",
        )
    if not book.job_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="직업이 선택되지 않았습니다",
        )

    pages = generate_dummy_story(db, book)

    return GenerateResponse(
        status=book.status,
        pages=[PageResponse.model_validate(p) for p in pages],
    )


@router.get("/{book_id}/pages", response_model=List[PageResponse])
def get_pages(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 페이지 목록 조회"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 조회할 수 있습니다",
        )

    pages = db.query(Page).filter(Page.book_id == book_id).order_by(Page.page_number).all()
    return [PageResponse.model_validate(p) for p in pages]
