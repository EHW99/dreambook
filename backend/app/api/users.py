"""사용자 API 라우터 — 프로필 수정, 비밀번호 변경, 회원 탈퇴"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import ChangePasswordRequest, UpdateProfileRequest, MessageResponse
from app.services.auth import validate_password, validate_name, validate_phone
from app.services.user import update_profile, change_password, delete_user_account

router = APIRouter(prefix="/api/users", tags=["users"])


@router.patch("/me", response_model=UserResponse)
def update_me(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 정보 수정 (이름, 전화번호)"""
    if req.name is not None and not validate_name(req.name):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이름을 입력해주세요 (1~50자)",
        )
    if req.phone is not None and not validate_phone(req.phone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="유효하지 않은 전화번호입니다",
        )

    user = update_profile(db, current_user, name=req.name, phone=req.phone)
    return user


@router.patch("/password", response_model=MessageResponse)
def update_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """비밀번호 변경"""
    # 새 비밀번호 길이 검증
    if not validate_password(req.new_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="새 비밀번호는 8자 이상이어야 합니다",
        )

    # 현재 비밀번호 확인 + 변경
    success = change_password(db, current_user, req.current_password, req.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 틀렸습니다",
        )

    return MessageResponse(message="비밀번호가 변경되었습니다")


@router.delete("/me", response_model=MessageResponse)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """회원 탈퇴 — CASCADE: 사용자의 모든 데이터 즉시 삭제"""
    delete_user_account(db, current_user)
    return MessageResponse(message="회원 탈퇴가 완료되었습니다")
