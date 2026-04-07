"""사진 API 라우터 — 업로드, 목록 조회, 삭제"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.photo import PhotoResponse
from app.services.photo import (
    validate_file_extension,
    validate_content_type,
    validate_file_size,
    validate_resolution,
    save_photo_file,
    create_photo,
    get_photo_count,
    get_photos_by_user,
    get_photo_by_id,
    delete_photo,
    MAX_PHOTOS_PER_USER,
)

router = APIRouter(prefix="/api/photos", tags=["photos"])


def photo_to_response(photo) -> dict:
    """Photo 모델 → 응답 dict (thumbnail_url 포함)"""
    return {
        "id": photo.id,
        "original_name": photo.original_name,
        "thumbnail_url": f"/uploads/{photo.file_path}",
        "width": photo.width,
        "height": photo.height,
        "file_size": photo.file_size,
        "created_at": photo.created_at,
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """사진 업로드 (multipart/form-data)"""
    # 1. 확장자 + Content-Type 검증
    if not validate_file_extension(file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="지원하지 않는 파일 형식입니다",
        )

    if not file.content_type or not validate_content_type(file.content_type):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="지원하지 않는 파일 형식입니다",
        )

    # 2. 파일 데이터 읽기
    file_data = await file.read()

    # 3. 크기 검증
    if not validate_file_size(file_data):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="파일 크기가 10MB를 초과합니다",
        )

    # 4. 해상도 읽기
    is_valid_res, width, height = validate_resolution(file_data)
    if not is_valid_res:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미지 파일을 읽을 수 없습니다",
        )

    # 5. 개수 제한 검증
    count = get_photo_count(db, current_user.id)
    if count >= MAX_PHOTOS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="최대 20장까지 등록 가능합니다",
        )

    # 6. 파일 저장
    file_name = save_photo_file(file_data, file.filename or "photo.png")

    # 7. DB 저장
    photo = create_photo(
        db=db,
        user_id=current_user.id,
        file_name=file_name,
        original_name=file.filename or "photo.png",
        file_size=len(file_data),
        width=width,
        height=height,
    )

    return photo_to_response(photo)


@router.get("", response_model=list[PhotoResponse])
def list_photos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 사진 목록 조회"""
    photos = get_photos_by_user(db, current_user.id)
    return [photo_to_response(p) for p in photos]


@router.delete("/{photo_id}")
def remove_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """사진 삭제 (DB + 파일)"""
    photo = get_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사진을 찾을 수 없습니다",
        )

    if photo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 사진만 삭제할 수 있습니다",
        )

    delete_photo(db, photo)
    return {"message": "사진이 삭제되었습니다"}
