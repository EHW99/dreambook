"""동화책 서비스 레이어"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.book import Book


def create_book(db: Session, user_id: int, voucher_id: int) -> Book:
    """동화책 레코드 생성 (draft 상태)"""
    book = Book(
        user_id=user_id,
        voucher_id=voucher_id,
        child_name="",  # 정보 입력 단계에서 설정
        status="draft",
        current_step=1,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
    """동화책 ID로 조회"""
    return db.query(Book).filter(Book.id == book_id).first()


def get_books_by_user(db: Session, user_id: int) -> List[Book]:
    """사용자의 동화책 목록 조회"""
    return db.query(Book).filter(Book.user_id == user_id).order_by(Book.created_at.desc()).all()


def update_book(db: Session, book: Book, **kwargs) -> Book:
    """동화책 정보 업데이트"""
    for key, value in kwargs.items():
        if value is not None and hasattr(book, key):
            setattr(book, key, value)
    book.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    """동화책 삭제 (draft 상태만)"""
    db.delete(book)
    db.commit()
