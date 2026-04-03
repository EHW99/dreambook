"""주문 관련 Pydantic 스키마"""
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ShippingInfo(BaseModel):
    """배송지 정보"""
    recipient_name: str
    recipient_phone: str
    postal_code: str
    address1: str
    address2: Optional[str] = None
    shipping_memo: Optional[str] = None

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("수령인 이름을 입력해주세요")
        if len(v) > 100:
            raise ValueError("수령인 이름은 최대 100자까지 입력 가능합니다")
        return v

    @field_validator("recipient_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("전화번호를 입력해주세요")
        # 한국 전화번호 형식 (010-xxxx-xxxx, 01012345678 등)
        cleaned = re.sub(r"[\s\-]", "", v)
        if not re.match(r"^0\d{9,10}$", cleaned):
            raise ValueError("올바른 전화번호 형식이 아닙니다 (예: 010-1234-5678)")
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("우편번호를 입력해주세요")
        if not re.match(r"^\d{5}$", v):
            raise ValueError("올바른 우편번호 형식이 아닙니다 (5자리 숫자)")
        return v

    @field_validator("address1")
    @classmethod
    def validate_address1(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("주소를 입력해주세요")
        if len(v) > 200:
            raise ValueError("주소는 최대 200자까지 입력 가능합니다")
        return v

    @field_validator("address2")
    @classmethod
    def validate_address2(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("상세주소는 최대 200자까지 입력 가능합니다")
        return v

    @field_validator("shipping_memo")
    @classmethod
    def validate_memo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("배송 메모는 최대 200자까지 입력 가능합니다")
        return v


class ShippingUpdateRequest(BaseModel):
    """배송지 변경 요청 — 변경할 필드만 전달"""
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    postal_code: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    shipping_memo: Optional[str] = None

    @field_validator("recipient_name")
    @classmethod
    def validate_recipient_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("수령인 이름을 입력해주세요")
            if len(v) > 100:
                raise ValueError("수령인 이름은 최대 100자까지 입력 가능합니다")
        return v

    @field_validator("recipient_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("전화번호를 입력해주세요")
            cleaned = re.sub(r"[\s\-]", "", v)
            if not re.match(r"^0\d{9,10}$", cleaned):
                raise ValueError("올바른 전화번호 형식이 아닙니다 (예: 010-1234-5678)")
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("우편번호를 입력해주세요")
            if not re.match(r"^\d{5}$", v):
                raise ValueError("올바른 우편번호 형식이 아닙니다 (5자리 숫자)")
        return v

    @field_validator("address1")
    @classmethod
    def validate_address1(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("주소를 입력해주세요")
            if len(v) > 200:
                raise ValueError("주소는 최대 200자까지 입력 가능합니다")
        return v

    @field_validator("address2")
    @classmethod
    def validate_address2(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("상세주소는 최대 200자까지 입력 가능합니다")
        return v

    @field_validator("shipping_memo")
    @classmethod
    def validate_memo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("배송 메모는 최대 200자까지 입력 가능합니다")
        return v


class OrderRequest(BaseModel):
    """주문 요청"""
    shipping: ShippingInfo


class EstimateItem(BaseModel):
    """견적 항목"""
    book_uid: Optional[str] = None
    page_count: Optional[int] = None
    quantity: int = 1
    unit_price: Optional[float] = None
    item_amount: Optional[float] = None


class EstimateResponse(BaseModel):
    """견적 응답"""
    product_amount: float = 0
    shipping_fee: float = 0
    packaging_fee: float = 0
    total_amount: float = 0
    paid_credit_amount: float = 0
    credit_balance: float = 0
    credit_sufficient: bool = True

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """주문 응답"""
    id: int
    book_id: int
    bookprint_order_uid: Optional[str] = None
    status: str
    status_code: int
    recipient_name: str
    recipient_phone: str
    postal_code: str
    address1: str
    address2: Optional[str] = None
    shipping_memo: Optional[str] = None
    total_amount: int
    ordered_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """주문 목록 항목"""
    id: int
    book_id: int
    book_title: Optional[str] = None
    status: str
    status_code: int
    recipient_name: str
    total_amount: int
    ordered_at: datetime

    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    """주문 상세"""
    id: int
    book_id: int
    bookprint_order_uid: Optional[str] = None
    status: str
    status_code: int
    recipient_name: str
    recipient_phone: str
    postal_code: str
    address1: str
    address2: Optional[str] = None
    shipping_memo: Optional[str] = None
    total_amount: int
    tracking_number: Optional[str] = None
    tracking_carrier: Optional[str] = None
    ordered_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
