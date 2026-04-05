"""이용권 관련 Pydantic 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VoucherPurchaseRequest(BaseModel):
    pass


class VoucherResponse(BaseModel):
    id: int
    price: int
    status: str
    book_id: Optional[int] = None
    purchased_at: datetime
    used_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
