"""이용권 서비스 레이어"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.voucher import Voucher

VOUCHER_PRICE = 9900  # AI 동화책 생성 이용권 (실물 책 별도)


def get_vouchers_by_user(db: Session, user_id: int) -> List[Voucher]:
    """사용자의 이용권 목록 조회"""
    return db.query(Voucher).filter(Voucher.user_id == user_id).order_by(Voucher.purchased_at.desc()).all()


def get_available_voucher(db: Session, user_id: int) -> Optional[Voucher]:
    """사용 가능한 이용권 하나 조회 (purchased 상태)"""
    return (
        db.query(Voucher)
        .filter(Voucher.user_id == user_id, Voucher.status == "purchased")
        .order_by(Voucher.purchased_at.asc())
        .first()
    )


def get_voucher_by_id(db: Session, voucher_id: int) -> Optional[Voucher]:
    """이용권 ID로 조회"""
    return db.query(Voucher).filter(Voucher.id == voucher_id).first()


def purchase_voucher(db: Session, user_id: int) -> Voucher:
    """이용권 구매 (목업 — 즉시 구매 완료)"""
    voucher = Voucher(
        user_id=user_id,
        price=VOUCHER_PRICE,
        status="purchased",
        purchased_at=datetime.now(timezone.utc),
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher


def use_voucher(db: Session, voucher: Voucher, book_id: int) -> Voucher:
    """이용권 사용 처리 (동화책에 연결)"""
    voucher.status = "used"
    voucher.book_id = book_id
    voucher.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(voucher)
    return voucher
