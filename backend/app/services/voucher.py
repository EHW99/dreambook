"""이용권 서비스 레이어"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict

from sqlalchemy.orm import Session, joinedload

from app.models.voucher import Voucher
from app.models.payment import Payment
from app.models.book import Book

VOUCHER_PRICE = 9900  # AI 동화책 생성 이용권 (실물 책 별도)

PAYMENT_METHODS = {
    "card": "신용/체크카드",
    "bank_transfer": "계좌이체",
    "kakao_pay": "카카오페이",
}


def get_vouchers_by_user(db: Session, user_id: int) -> List[Voucher]:
    """사용자의 이용권 목록 조회 (책 제목 포함)"""
    return (
        db.query(Voucher)
        .outerjoin(Book, Voucher.book_id == Book.id)
        .filter(Voucher.user_id == user_id)
        .order_by(Voucher.purchased_at.desc())
        .all()
    )


def get_voucher_summary(db: Session, user_id: int) -> Dict[str, int]:
    """이용권 요약 (보유/사용/환불/전체)"""
    vouchers = db.query(Voucher).filter(Voucher.user_id == user_id).all()
    available = sum(1 for v in vouchers if v.status == "purchased")
    used = sum(1 for v in vouchers if v.status == "used")
    refunded = sum(1 for v in vouchers if v.status == "refunded")
    return {
        "available": available,
        "used": used,
        "refunded": refunded,
        "total": len(vouchers),
    }


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


def purchase_voucher(db: Session, user_id: int, quantity: int = 1, payment_method: str = "card") -> tuple[Payment, List[Voucher]]:
    """이용권 구매 — 결제 기록 + 이용권 N장 발급"""
    now = datetime.now(timezone.utc)
    total_amount = VOUCHER_PRICE * quantity
    merchant_uid = f"ORD-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # 결제 기록 생성
    payment = Payment(
        user_id=user_id,
        amount=total_amount,
        quantity=quantity,
        payment_method=payment_method,
        status="completed",
        merchant_uid=merchant_uid,
        paid_at=now,
    )
    db.add(payment)
    db.flush()  # payment.id 확보

    # 이용권 발급
    vouchers = []
    for _ in range(quantity):
        voucher = Voucher(
            user_id=user_id,
            payment_id=payment.id,
            price=VOUCHER_PRICE,
            status="purchased",
            purchased_at=now,
        )
        db.add(voucher)
        vouchers.append(voucher)

    db.commit()
    db.refresh(payment)
    for v in vouchers:
        db.refresh(v)

    return payment, vouchers


def use_voucher(db: Session, voucher: Voucher, book_id: int) -> Voucher:
    """이용권 사용 처리 (동화책에 연결)"""
    voucher.status = "used"
    voucher.book_id = book_id
    voucher.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(voucher)
    return voucher


def refund_voucher(db: Session, voucher: Voucher) -> Voucher:
    """미사용 이용권 환불"""
    if voucher.status != "purchased":
        raise ValueError("사용된 이용권은 환불할 수 없습니다")

    now = datetime.now(timezone.utc)
    voucher.status = "refunded"
    voucher.used_at = now  # 환불 처리 시간 기록

    # 결제 기록에도 환불 반영 (해당 결제의 모든 이용권이 환불되었으면 결제도 환불 상태로)
    if voucher.payment_id:
        payment = db.query(Payment).filter(Payment.id == voucher.payment_id).first()
        if payment:
            siblings = db.query(Voucher).filter(
                Voucher.payment_id == payment.id,
                Voucher.id != voucher.id,
                Voucher.status == "purchased",
            ).count()
            # 이 결제로 발급된 모든 이용권이 환불/사용되었으면 결제도 환불 처리
            active_siblings = db.query(Voucher).filter(
                Voucher.payment_id == payment.id,
                Voucher.status == "purchased",
                Voucher.id != voucher.id,
            ).count()
            if active_siblings == 0:
                all_refunded = db.query(Voucher).filter(
                    Voucher.payment_id == payment.id,
                    Voucher.status != "refunded",
                    Voucher.id != voucher.id,
                ).count() == 0
                # 전부 환불이면 결제도 refunded
                if all_refunded or db.query(Voucher).filter(Voucher.payment_id == payment.id).count() == 1:
                    payment.status = "refunded"
                    payment.refunded_at = now

    db.commit()
    db.refresh(voucher)
    return voucher


def get_payments_by_user(db: Session, user_id: int) -> List[Payment]:
    """사용자의 결제 내역 조회"""
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.paid_at.desc())
        .all()
    )
