"""사진 관련 Pydantic 스키마"""
from datetime import datetime
from pydantic import BaseModel


class PhotoResponse(BaseModel):
    id: int
    original_name: str
    thumbnail_url: str
    width: int
    height: int
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
