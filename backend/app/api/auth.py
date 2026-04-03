"""인증 API 라우터 — 회원가입, 로그인, 토큰 갱신, 내 정보 조회"""
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    AccessTokenResponse,
    UserResponse,
)
from app.services.auth import (
    validate_email,
    validate_password,
    get_user_by_email,
    get_user_by_id,
    create_user,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

REFRESH_TOKEN_COOKIE = "refresh_token"
REFRESH_TOKEN_MAX_AGE = get_settings().REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 초 단위


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """회원가입"""
    # 이메일 형식 검증
    if not validate_email(req.email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="유효하지 않은 이메일 형식입니다",
        )

    # 비밀번호 길이 검증
    if not validate_password(req.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호는 8자 이상이어야 합니다",
        )

    # 이메일 중복 검증
    if get_user_by_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다",
        )

    user = create_user(db, req.email, req.password)
    return user


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """로그인 — Access Token 응답 + Refresh Token httpOnly 쿠키"""
    user = get_user_by_email(db, req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 틀렸습니다",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Refresh Token을 httpOnly 쿠키로 설정
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        path="/api/auth/refresh",
        max_age=REFRESH_TOKEN_MAX_AGE,
        secure=False,  # 로컬 개발용. 프로덕션에서는 True
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    request: Request,
    db: Session = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None),
):
    """Refresh Token(httpOnly 쿠키)으로 Access Token 갱신"""
    # 쿠키에서 refresh token 읽기
    token = refresh_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )

    # DB에서 사용자 존재 여부 확인 (탈퇴한 사용자의 refresh token 차단)
    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )

    return AccessTokenResponse(
        access_token=create_access_token(int(user_id)),
    )


@router.post("/logout")
def logout(response: Response):
    """로그아웃 — Refresh Token 쿠키 삭제"""
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path="/api/auth/refresh",
    )
    return {"message": "로그아웃 완료"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자 정보 조회"""
    return current_user
