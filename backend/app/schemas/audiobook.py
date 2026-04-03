"""오디오북 관련 Pydantic 스키마"""
from typing import Optional, List
from pydantic import BaseModel


class AudioPageData(BaseModel):
    page_number: int
    text_content: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class AudioBookData(BaseModel):
    book_title: Optional[str] = None
    child_name: str
    total_pages: int
    pages: List[AudioPageData]

    model_config = {"from_attributes": True}
