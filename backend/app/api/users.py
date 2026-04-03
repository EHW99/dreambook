"""사용자 API 라우터 — 비밀번호 변경, 회원 탈퇴"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, MessageResponse
from app.services.auth import validate_password
from app.services.user import change_password, delete_user_account

router = APIRouter(prefix="/api/users", tags=["users"])


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
