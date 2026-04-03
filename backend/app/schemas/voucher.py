"""이용권 관련 Pydantic 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class VoucherPurchaseRequest(BaseModel):
    voucher_type: str

    @field_validator("voucher_type")
    @classmethod
    def validate_voucher_type(cls, v: str) -> str:
        valid_types = {"story_only", "story_and_print"}
        if v not in valid_types:
            raise ValueError("유효하지 않은 이용권 종류입니다")
        return v


class VoucherResponse(BaseModel):
    id: int
    voucher_type: str
    price: int
    status: str
    book_id: Optional[int] = None
    purchased_at: datetime
    used_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
