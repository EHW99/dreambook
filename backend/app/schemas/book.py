"""동화책 관련 Pydantic 스키마"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class BookCreateRequest(BaseModel):
    voucher_id: int


VALID_STORY_STYLES = {"dreaming_today", "future_me"}
VALID_ART_STYLES = {"watercolor", "pencil", "crayon", "3d", "cartoon"}
VALID_STATUSES = {"draft", "character_confirmed", "generating", "editing", "completed"}


class BookUpdateRequest(BaseModel):
    child_name: Optional[str] = None
    child_birth_date: Optional[date] = None
    photo_id: Optional[int] = None
    job_category: Optional[str] = None
    job_name: Optional[str] = None
    story_style: Optional[str] = None
    art_style: Optional[str] = None
    current_step: Optional[int] = None
    status: Optional[str] = None

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

    @field_validator("story_style")
    @classmethod
    def validate_story_style(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STORY_STYLES:
            raise ValueError(f"유효하지 않은 동화 스타일입니다. 가능한 값: {', '.join(VALID_STORY_STYLES)}")
        return v

    @field_validator("art_style")
    @classmethod
    def validate_art_style(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ART_STYLES:
            raise ValueError(f"유효하지 않은 그림체입니다. 가능한 값: {', '.join(VALID_ART_STYLES)}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"유효하지 않은 상태입니다. 가능한 값: {', '.join(VALID_STATUSES)}")
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
