"""동화책 관련 Pydantic 스키마"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class BookCreateRequest(BaseModel):
    voucher_id: int


class BookUpdateRequest(BaseModel):
    child_name: Optional[str] = None
    child_birth_date: Optional[date] = None
    photo_id: Optional[int] = None
    job_category: Optional[str] = None
    job_name: Optional[str] = None
    current_step: Optional[int] = None

    @field_validator("child_name")
    @classmethod
    def validate_child_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError("아이 이름을 입력해주세요")
            if len(v) > 20:
                raise ValueError("아이 이름은 최대 20자까지 입력 가능합니다")
        return v


class BookResponse(BaseModel):
    id: int
    voucher_id: Optional[int] = None
    child_name: str
    child_birth_date: Optional[date] = None
    photo_id: Optional[int] = None
    job_category: Optional[str] = None
    job_name: Optional[str] = None
    story_style: Optional[str] = None
    art_style: Optional[str] = None
    page_count: int
    book_spec_uid: str
    plot_input: Optional[str] = None
    status: str
    current_step: int
    title: Optional[str] = None
    story_regen_count: int
    character_regen_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    id: int
    child_name: str
    job_name: Optional[str] = None
    status: str
    current_step: int
    title: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
