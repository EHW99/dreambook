"""사용자 관련 Pydantic 스키마"""
from typing import Optional
from pydantic import BaseModel


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
