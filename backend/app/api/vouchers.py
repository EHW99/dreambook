"""이용권 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.voucher import VoucherPurchaseRequest, VoucherResponse
from app.services.voucher import get_vouchers_by_user, purchase_voucher

router = APIRouter(prefix="/api/vouchers")


@router.get("", response_model=List[VoucherResponse])
def list_vouchers(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 이용권 목록 조회"""
    vouchers = get_vouchers_by_user(db, user.id)
    return vouchers


@router.post("/purchase", response_model=VoucherResponse, status_code=status.HTTP_201_CREATED)
def purchase(
    req: VoucherPurchaseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """이용권 구매 (목업 — 즉시 구매 완료)"""
    voucher = purchase_voucher(db, user.id)
    return voucher
