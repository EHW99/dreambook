"""이용권 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.voucher import (
    VoucherPurchaseRequest,
    VoucherResponse,
    VoucherSummaryResponse,
    PaymentResponse,
    PurchaseResultResponse,
)
from app.services.voucher import (
    get_vouchers_by_user,
    get_voucher_summary,
    get_voucher_by_id,
    get_payments_by_user,
    purchase_voucher,
    refund_voucher,
)

router = APIRouter(prefix="/api/vouchers")


@router.get("", response_model=List[VoucherResponse])
def list_vouchers(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 이용권 목록 조회"""
    vouchers = get_vouchers_by_user(db, user.id)
    result = []
    for v in vouchers:
        data = VoucherResponse.model_validate(v)
        # 사용된 이용권이면 책 제목 포함
        if v.book:
            data.book_title = v.book.title or v.book.child_name
        result.append(data)
    return result


@router.get("/summary", response_model=VoucherSummaryResponse)
def voucher_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """이용권 요약 (보유/사용/환불/전체)"""
    return get_voucher_summary(db, user.id)


@router.get("/payments", response_model=List[PaymentResponse])
def list_payments(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """결제 내역 조회"""
    return get_payments_by_user(db, user.id)


@router.post("/purchase", response_model=PurchaseResultResponse, status_code=status.HTTP_201_CREATED)
def purchase(
    req: VoucherPurchaseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """이용권 구매 (가상 결제)"""
    payment, vouchers = purchase_voucher(
        db, user.id,
        quantity=req.quantity,
        payment_method=req.payment_method,
    )

    voucher_responses = []
    for v in vouchers:
        data = VoucherResponse.model_validate(v)
        voucher_responses.append(data)

    return PurchaseResultResponse(
        payment=PaymentResponse.model_validate(payment),
        vouchers=voucher_responses,
    )


@router.post("/{voucher_id}/refund", response_model=VoucherResponse)
def refund(
    voucher_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """이용권 환불 (미사용만 가능)"""
    voucher = get_voucher_by_id(db, voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="이용권을 찾을 수 없습니다")
    if voucher.user_id != user.id:
        raise HTTPException(status_code=403, detail="본인의 이용권만 환불할 수 있습니다")
    if voucher.status != "purchased":
        raise HTTPException(status_code=400, detail="미사용 이용권만 환불할 수 있습니다")

    try:
        result = refund_voucher(db, voucher)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return VoucherResponse.model_validate(result)
