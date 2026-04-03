"""사용자 서비스 — 비밀번호 변경, 회원 탈퇴"""
import os

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.photo import Photo
from app.services.auth import verify_password, hash_password


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """비밀번호 변경. 현재 비밀번호 검증 후 새 비밀번호로 변경."""
    if not verify_password(current_password, user.password_hash):
        return False

    user.password_hash = hash_password(new_password)
    db.commit()
    return True


def delete_user_account(db: Session, user: User) -> None:
    """회원 탈퇴 — 사진 파일 삭제 + DB CASCADE 삭제"""
    # 사진 파일 삭제
    photos = db.query(Photo).filter(Photo.user_id == user.id).all()
    for photo in photos:
        try:
            if os.path.exists(photo.file_path):
                os.remove(photo.file_path)
        except OSError:
            pass  # 파일 삭제 실패해도 계속 진행

    # DB에서 사용자 삭제 (CASCADE로 관련 레코드 모두 삭제)
    db.delete(user)
    db.commit()
