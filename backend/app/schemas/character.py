"""캐릭터 시트 관련 Pydantic 스키마"""
from datetime import datetime
from pydantic import BaseModel


class CharacterSheetResponse(BaseModel):
    id: int
    book_id: int
    image_path: str
    art_style: str | None = None
    generation_index: int
    is_selected: bool
    created_at: datetime

    model_config = {"from_attributes": True}
