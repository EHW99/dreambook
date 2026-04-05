"""이용권 관련 Pydantic 스키마"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class VoucherPurchaseRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=10)
    payment_method: str = Field(default="card")  # card, bank_transfer, kakao_pay


class VoucherResponse(BaseModel):
    id: int
    price: int
    status: str
    book_id: Optional[int] = None
    payment_id: Optional[int] = None
    purchased_at: datetime
    used_at: Optional[datetime] = None
    book_title: Optional[str] = None  # 사용된 이용권의 책 제목

    model_config = {"from_attributes": True}


class VoucherSummaryResponse(BaseModel):
    available: int
    used: int
    refunded: int
    total: int


class PaymentResponse(BaseModel):
    id: int
    amount: int
    quantity: int
    payment_method: str
    status: str
    merchant_uid: str
    paid_at: datetime
    refunded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PurchaseResultResponse(BaseModel):
    payment: PaymentResponse
    vouchers: List[VoucherResponse]
