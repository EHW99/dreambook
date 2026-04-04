"""동화책 관련 Pydantic 스키마"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class BookCreateRequest(BaseModel):
    voucher_id: int


VALID_STORY_STYLES = {"dreaming_today", "future_me"}
VALID_ART_STYLES = {"watercolor", "pencil", "crayon", "3d", "cartoon"}
VALID_STATUSES = {"draft", "character_confirmed", "generating", "editing", "completed"}
def _get_valid_book_spec_uids() -> set[str]:
    """캐시된 판형 UID 목록 반환"""
    from app.services.bookprint import get_book_specs
    specs = get_book_specs()
    return set(specs.keys()) if specs else {"SQUAREBOOK_HC", "PHOTOBOOK_A4_SC", "PHOTOBOOK_A5_SC"}


def _get_book_spec_page_range(spec_uid: str) -> tuple[int, int] | None:
    """캐시된 판형의 페이지 범위 반환"""
    from app.services.bookprint import get_book_specs
    specs = get_book_specs()
    if spec_uid in specs:
        return (specs[spec_uid]["page_min"], specs[spec_uid]["page_max"])
    return None


class BookUpdateRequest(BaseModel):
    child_name: Optional[str] = None
    child_birth_date: Optional[date] = None
    photo_id: Optional[int] = None
    job_category: Optional[str] = None
    job_name: Optional[str] = None
    story_style: Optional[str] = None
    art_style: Optional[str] = None
    page_count: Optional[int] = None
    book_spec_uid: Optional[str] = None
    plot_input: Optional[str] = None
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

    @field_validator("page_count")
    @classmethod
    def validate_page_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v % 2 != 0:
                raise ValueError("페이지 수는 2의 배수여야 합니다")
            if v < 24:
                raise ValueError("페이지 수는 최소 24페이지 이상이어야 합니다")
            if v > 200:
                raise ValueError("페이지 수는 최대 200페이지까지 가능합니다")
        return v

    @field_validator("book_spec_uid")
    @classmethod
    def validate_book_spec_uid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = _get_valid_book_spec_uids()
            if v not in valid:
                raise ValueError(f"유효하지 않은 판형입니다. 가능한 값: {', '.join(valid)}")
        return v

    @field_validator("plot_input")
    @classmethod
    def validate_plot_input(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 1000:
            raise ValueError("줄거리는 최대 1000자까지 입력 가능합니다")
        return v

    @model_validator(mode="after")
    def validate_page_count_for_spec(self):
        """판형별 페이지 수 범위 교차 검증"""
        if self.page_count is not None and self.book_spec_uid is not None:
            page_range = _get_book_spec_page_range(self.book_spec_uid)
            if page_range:
                min_pages, max_pages = page_range
                if self.page_count < min_pages or self.page_count > max_pages:
                    raise ValueError(
                        f"{self.book_spec_uid} 판형의 페이지 수는 {min_pages}~{max_pages}페이지여야 합니다"
                    )
        return self

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
    art_style: Optional[str] = None
    status: str
    current_step: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PageImageResponse(BaseModel):
    id: int
    image_path: str
    generation_index: int
    is_selected: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PageResponse(BaseModel):
    id: int
    book_id: int
    page_number: int
    page_type: str
    scene_description: Optional[str] = None
    text_content: Optional[str] = None
    image_regen_count: int
    images: list[PageImageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerateResponse(BaseModel):
    status: str
    pages: list[PageResponse]

    model_config = {"from_attributes": True}


class PageTextUpdateRequest(BaseModel):
    text_content: str


class RegenerateStoryResponse(BaseModel):
    status: str
    story_regen_count: int
    pages: list[PageResponse]

    model_config = {"from_attributes": True}


class RegenerateImageResponse(BaseModel):
    page_id: int
    image_regen_count: int
    images: list[PageImageResponse]

    model_config = {"from_attributes": True}


class ImageSelectResponse(BaseModel):
    id: int
    is_selected: bool

    model_config = {"from_attributes": True}
