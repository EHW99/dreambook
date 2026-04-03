"""인증 관련 Pydantic 스키마"""
from datetime import datetime
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str


class SignupResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """로그인 응답 — access_token은 JSON, refresh_token은 httpOnly 쿠키로도 전달"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
