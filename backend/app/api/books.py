"""동화책 API 라우터"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

logger = logging.getLogger(__name__)

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.page import Page
from app.models.page_image import PageImage
from app.schemas.book import (
    BookCreateRequest, BookUpdateRequest, BookResponse, BookListResponse,
    GenerateResponse, PageResponse, PageImageResponse,
    PageTextUpdateRequest, RegenerateStoryResponse, RegenerateImageResponse,
    ImageSelectResponse,
)
from app.schemas.audiobook import AudioBookData, AudioPageData
from app.services.book import create_book, get_book_by_id, get_books_by_user, update_book, delete_book
from app.services.generate import generate_story, generate_story_only, generate_illustrations, generate_cover_image
from app.services.ai_story import StoryGenerationError
from app.services.ai_illustration import generate_illustration_or_dummy
from app.services.voucher import get_voucher_by_id, use_voucher

router = APIRouter(prefix="/api/books")


@router.get("/specs")
def list_book_specs():
    """판형 목록 조회 (캐시된 데이터)"""
    from app.services.bookprint import get_book_specs
    specs = get_book_specs()
    return [
        {
            "uid": uid,
            "name": info["name"],
            "width_mm": info["width_mm"],
            "height_mm": info["height_mm"],
            "page_min": info["page_min"],
            "page_max": info["page_max"],
            "cover_type": info.get("cover_type", ""),
            "binding_type": info.get("binding_type", ""),
        }
        for uid, info in specs.items()
    ]


@router.get("", response_model=List[BookListResponse])
def list_books(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 동화책 목록 조회"""
    books = get_books_by_user(db, user.id)
    return books


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create(
    req: BookCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 생성 (이용권 연결)"""
    # 이용권 확인
    voucher = get_voucher_by_id(db, req.voucher_id)
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이용권을 찾을 수 없습니다",
        )
    if voucher.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 이용권만 사용할 수 있습니다",
        )
    if voucher.status != "purchased":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용된 이용권입니다",
        )

    # 동화책 생성
    book = create_book(db, user.id, voucher.id)

    # 이용권 사용 처리
    use_voucher(db, voucher, book.id)

    # book 새로고침 (voucher 연결 후)
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 상세 조회"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 조회할 수 있습니다",
        )
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update(
    book_id: int,
    req: BookUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 정보 수정 (단계별 저장)"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 수정할 수 있습니다",
        )

    # photo_id 유효성 검사
    if req.photo_id is not None:
        from app.models.photo import Photo
        photo = db.query(Photo).filter(Photo.id == req.photo_id, Photo.user_id == user.id).first()
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사진을 찾을 수 없습니다",
            )

    # step 5→6 전환 시 캐릭터 선택 여부 서버 측 검증
    if req.current_step is not None and req.current_step >= 6 and book.current_step <= 5:
        from app.models.character_sheet import CharacterSheet
        selected = db.query(CharacterSheet).filter(
            CharacterSheet.book_id == book.id,
            CharacterSheet.is_selected == True,
        ).first()
        if not selected:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="캐릭터를 선택해주세요",
            )

    update_data = req.model_dump(exclude_unset=True)
    book = update_book(db, book, **update_data)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
def delete(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 삭제 — 주문된 책은 주문 취소 후 삭제"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 삭제할 수 있습니다",
        )

    # 주문이 있으면 취소 먼저
    from app.models.order import Order
    order = db.query(Order).filter(Order.book_id == book.id).first()
    if order and order.bookprint_order_uid:
        try:
            from app.services.bookprint import BookPrintService, BookPrintAPIError
            import asyncio
            service = BookPrintService()
            asyncio.get_event_loop().run_until_complete(
                service.cancel_order(order.bookprint_order_uid)
            )
            asyncio.get_event_loop().run_until_complete(service.close())
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"주문 취소 실패 (무시): {e}")
    if order:
        db.delete(order)
        db.flush()

    delete_book(db, book)
    return {"message": "동화책이 삭제되었습니다"}


@router.post("/{book_id}/generate", response_model=GenerateResponse)
def generate(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """더미 스토리+이미지 생성 (Phase 2)"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 생성할 수 있습니다",
        )

    # 이미 생성된 동화책은 재생성 방어
    if book.status not in ("draft", "character_confirmed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미 생성된 동화책입니다",
        )

    # 필수 정보 검증
    if not book.child_name or book.child_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="아이 이름이 입력되지 않았습니다",
        )
    if not book.job_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="직업이 선택되지 않았습니다",
        )

    try:
        pages = generate_story(db, book)
    except StoryGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스토리 생성에 실패했습니다: {str(e)}",
        )

    return GenerateResponse(
        status=book.status,
        pages=[PageResponse.model_validate(p) for p in pages],
    )


@router.post("/{book_id}/generate-story", response_model=GenerateResponse)
def generate_story_only_endpoint(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """1단계: 스토리 텍스트만 생성 (이미지 없이, 빠름)"""
    book = _get_book_or_403(db, book_id, user)

    if book.status not in ("draft", "character_confirmed"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미 생성된 동화책입니다",
        )
    if not book.child_name or not book.child_name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="아이 이름이 입력되지 않았습니다",
        )
    if not book.job_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="직업이 선택되지 않았습니다",
        )

    try:
        pages = generate_story_only(db, book)
    except StoryGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스토리 생성에 실패했습니다: {str(e)}",
        )

    return GenerateResponse(
        status=book.status,
        pages=[PageResponse.model_validate(p) for p in pages],
    )


@router.post("/{book_id}/generate-illustrations", response_model=GenerateResponse)
def generate_illustrations_endpoint(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """2단계: 확정된 텍스트 기반으로 일러스트 생성"""
    book = _get_book_or_403(db, book_id, user)

    if book.status not in ("story_generated", "editing"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="스토리가 먼저 생성되어야 합니다",
        )

    # 재생성(editing 상태)일 때 횟수 체크
    if book.status == "editing":
        if book.illust_regen_count >= 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="일러스트 재생성 횟수를 모두 사용했습니다 (최대 2회)",
            )
        book.illust_regen_count += 1
        db.commit()

    pages = generate_illustrations(db, book)

    return GenerateResponse(
        status=book.status,
        pages=[PageResponse.model_validate(p) for p in pages],
    )


@router.post("/{book_id}/generate-plots")
def generate_plots_endpoint(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """줄거리 후보 4개 생성 (LLM)"""
    book = _get_book_or_403(db, book_id, user)

    from app.services.ai_plot import generate_plots
    from app.services.generate import _calc_child_age

    child_age = _calc_child_age(book.child_birth_date)
    child_gender = book.child_gender or "male"

    try:
        result = generate_plots(
            child_name=book.child_name,
            job_name=book.job_name or "직업",
            child_age=child_age,
            child_gender=child_gender,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"줄거리 생성에 실패했습니다: {str(e)}",
        )

    return result


@router.post("/{book_id}/generate-cover")
def generate_cover_endpoint(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """표지 이미지 생성"""
    book = _get_book_or_403(db, book_id, user)

    image_path = generate_cover_image(db, book)

    if image_path:
        book.cover_image_path = image_path
        db.commit()

    return {
        "image_path": image_path,
        "message": "표지 이미지가 생성되었습니다",
    }


@router.get("/{book_id}/pages", response_model=List[PageResponse])
def get_pages(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 페이지 목록 조회"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동화책을 찾을 수 없습니다",
        )
    if book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 동화책만 조회할 수 있습니다",
        )

    pages = db.query(Page).filter(Page.book_id == book_id).order_by(Page.page_number).all()
    return [PageResponse.model_validate(p) for p in pages]


def _get_book_or_403(db: Session, book_id: int, user: User):
    """동화책 조회 + 소유자 확인 헬퍼"""
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="동화책을 찾을 수 없습니다")
    if book.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인의 동화책만 접근할 수 있습니다")
    return book


@router.patch("/{book_id}/pages/{page_id}", response_model=PageResponse)
def update_page_text(
    book_id: int,
    page_id: int,
    req: PageTextUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """페이지 텍스트 인라인 편집"""
    book = _get_book_or_403(db, book_id, user)

    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    from datetime import datetime, timezone
    page.text_content = req.text_content
    page.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(page)
    return PageResponse.model_validate(page)


@router.post("/{book_id}/regenerate-story", response_model=RegenerateStoryResponse)
def regenerate_story(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """스토리 재생성 (텍스트만, 일러스트는 별도)"""
    book = _get_book_or_403(db, book_id, user)

    # 확정/완료된 책은 재생성 불가
    if book.status in ("confirmed", "completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="확정된 동화책은 재생성할 수 없습니다",
        )

    if book.story_regen_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="스토리 재생성 횟수를 모두 사용했습니다 (최대 3회)",
        )

    # 횟수 증가
    book.story_regen_count += 1

    # 스토리 텍스트만 재생성 (일러스트는 별도 단계에서)
    prev_status = book.status
    try:
        pages = generate_story_only(db, book)
    except StoryGenerationError as e:
        # 실패 시 횟수 롤백
        book.story_regen_count -= 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스토리 생성에 실패했습니다: {str(e)}",
        )

    # 편집 페이지에서 재생성한 경우 status를 editing으로 복원
    # (generate_story_only가 "story_generated"로 바꾸므로)
    if prev_status == "editing":
        book.status = "editing"
        db.commit()

    return RegenerateStoryResponse(
        status=book.status,
        story_regen_count=book.story_regen_count,
        pages=[PageResponse.model_validate(p) for p in pages],
    )


@router.post("/{book_id}/pages/{page_id}/regenerate-image", response_model=RegenerateImageResponse)
def regenerate_image(
    book_id: int,
    page_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """페이지 이미지 재생성 (Phase 2: 더미, 갤러리 방식)"""
    book = _get_book_or_403(db, book_id, user)

    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    if page.image_regen_count >= 4:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="이미지 재생성 횟수를 모두 사용했습니다 (최대 4회)",
        )

    from datetime import datetime, timezone
    import os
    now = datetime.now(timezone.utc)

    # 기존 이미지 모두 선택 해제
    for img in page.images:
        img.is_selected = False

    new_index = len(page.images)

    # AI 일러스트 생성 시도
    image_path = None

    # 캐릭터 시트 조회 (파일 시스템 경로로 변환)
    from app.services.generate import _get_selected_character_sheet_path, _calc_child_age
    char_path = _get_selected_character_sheet_path(db, book.id)

    if page.scene_description:
        child_age = _calc_child_age(book.child_birth_date)
        child_gender = book.child_gender or "male"
        ai_bytes = generate_illustration_or_dummy(
            character_sheet_path=char_path or "",
            scene_description=page.scene_description,
            art_style=book.art_style or "watercolor",
            child_name=book.child_name,
            job_name=book.job_name or "직업",
            child_age=child_age,
            child_gender=child_gender,
            job_name_en=book.job_name_en or "",
            job_outfit=book.job_outfit or "",
        )
        if ai_bytes:
            from app.services.photo import UPLOAD_DIR, ensure_upload_dir
            ensure_upload_dir()
            filename = f"ai_illust_book{book.id}_page{page.page_number}_v{new_index}.png"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(ai_bytes)
            image_path = filepath

    # AI 실패 시 placeholder 폴백
    if not image_path:
        from app.services.generate import _create_placeholder_image
        image_path = _create_placeholder_image(
            page.page_number, f"Regen v{new_index}", book.id
        )

    new_image = PageImage(
        page_id=page.id,
        image_path=image_path,
        generation_index=new_index,
        is_selected=True,
        created_at=now,
    )
    db.add(new_image)

    page.image_regen_count += 1
    page.updated_at = now
    db.commit()
    db.refresh(page)

    return RegenerateImageResponse(
        page_id=page.id,
        image_regen_count=page.image_regen_count,
        images=[PageImageResponse.model_validate(img) for img in page.images],
    )


@router.get("/{book_id}/pages/{page_id}/images", response_model=List[PageImageResponse])
def get_page_images(
    book_id: int,
    page_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """페이지 이미지 갤러리 조회"""
    book = _get_book_or_403(db, book_id, user)

    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    return [PageImageResponse.model_validate(img) for img in page.images]


@router.patch("/{book_id}/pages/{page_id}/images/{image_id}/select", response_model=ImageSelectResponse)
def select_page_image(
    book_id: int,
    page_id: int,
    image_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """이미지 선택 (갤러리에서 하나를 선택)"""
    book = _get_book_or_403(db, book_id, user)

    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="페이지를 찾을 수 없습니다")

    target_image = db.query(PageImage).filter(
        PageImage.id == image_id,
        PageImage.page_id == page_id,
    ).first()
    if not target_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지를 찾을 수 없습니다")

    # 모든 이미지 선택 해제 후 타겟만 선택
    for img in page.images:
        img.is_selected = False
    target_image.is_selected = True

    db.commit()
    db.refresh(target_image)

    return ImageSelectResponse(id=target_image.id, is_selected=True)


@router.get("/{book_id}/audio-data", response_model=AudioBookData)
def get_audio_data(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """오디오북용 페이지별 텍스트 + 이미지 URL 반환"""
    book = _get_book_or_403(db, book_id, user)

    pages = db.query(Page).filter(Page.book_id == book_id).order_by(Page.page_number).all()

    audio_pages = []
    for page in pages:
        # 선택된 이미지의 경로를 찾음
        selected_image = None
        for img in page.images:
            if img.is_selected:
                selected_image = img.image_path
                break

        audio_pages.append(AudioPageData(
            page_number=page.page_number,
            text_content=page.text_content,
            image_url=selected_image,
        ))

    return AudioBookData(
        book_title=book.title,
        child_name=book.child_name,
        total_pages=len(audio_pages),
        pages=audio_pages,
    )


@router.get("/{book_id}/thumbnails")
def get_thumbnails(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """완성된 책의 렌더링 썸네일 목록 반환"""
    import os
    from app.models.book import Book

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="동화책을 찾을 수 없습니다")
    if book.user_id != user.id:
        raise HTTPException(status_code=403, detail="본인의 동화책만 접근할 수 있습니다")

    if not book.thumbnail_dir or not os.path.isdir(book.thumbnail_dir):
        raise HTTPException(status_code=404, detail="썸네일이 아직 생성되지 않았습니다")

    # URL 경로 생성 (uploads/ 기준 상대 경로)
    thumb_dir = book.thumbnail_dir
    cover_path = os.path.join(thumb_dir, "cover.jpg")
    cover_url = None
    if os.path.exists(cover_path):
        # /uploads/thumbnails/bk_xxx/cover.jpg 형태로 변환
        from app.services.photo import UPLOAD_DIR
        rel = os.path.relpath(cover_path, UPLOAD_DIR).replace("\\", "/")
        cover_url = f"/uploads/{rel}"

    pages = []
    for pn in range(24):
        page_path = os.path.join(thumb_dir, f"{pn}.jpg")
        if os.path.exists(page_path):
            rel = os.path.relpath(page_path, UPLOAD_DIR).replace("\\", "/")
            pages.append(f"/uploads/{rel}")

    return {"cover": cover_url, "pages": pages}


@router.post("/{book_id}/confirm")
async def confirm_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동화책 확정 — Book Print API 업로드 + 썸네일 생성 + 수정 불가 전환"""
    from app.models.book import Book
    from app.services.bookprint import BookPrintService, BookPrintAPIError
    from app.services.photo import UPLOAD_DIR

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="동화책을 찾을 수 없습니다")
    if book.user_id != user.id:
        raise HTTPException(status_code=403, detail="본인의 동화책만 확정할 수 있습니다")
    if book.status != "editing":
        raise HTTPException(status_code=400, detail="편집 중인 동화책만 확정할 수 있습니다")

    # 페이지 데이터 조회 (orders.py의 _get_pages_data와 동일 로직)
    from app.models.page import Page
    pages = db.query(Page).filter(Page.book_id == book.id).order_by(Page.page_number).all()
    pages_data = []
    for page in pages:
        selected_image = None
        for img in page.images:
            if img.is_selected:
                selected_image = img
                break
        image_path = ""
        if selected_image and selected_image.image_path:
            ip = selected_image.image_path
            if os.path.isabs(ip) and os.path.exists(ip):
                image_path = ip
            elif ip.startswith("/"):
                local = os.path.join(UPLOAD_DIR, os.path.basename(ip))
                if os.path.exists(local):
                    image_path = local
            elif os.path.exists(ip):
                image_path = ip
        pages_data.append({
            "text": page.text_content or "",
            "image_path": image_path,
            "page_number": page.page_number,
            "page_type": page.page_type,
        })

    # 표지 이미지
    cover_image_path = book.cover_image_path
    if not cover_image_path or not os.path.exists(cover_image_path):
        for pd in pages_data:
            if pd.get("page_type") == "illustration" and pd.get("image_path"):
                if os.path.exists(pd["image_path"]):
                    cover_image_path = pd["image_path"]
                    break

    # Book Print API 업로드 + 썸네일
    service = BookPrintService()
    try:
        book_uid = await service.upload_book(
            title=book.title or f"{book.child_name}의 동화책",
            book_spec_uid=book.book_spec_uid,
            pages_data=pages_data,
            cover_image_path=cover_image_path,
            child_name=book.child_name,
        )
        book.bookprint_book_uid = book_uid

        # 썸네일 다운로드
        thumbnail_dir = os.path.join(UPLOAD_DIR, "thumbnails", book_uid)
        await service.download_thumbnails(book_uid, thumbnail_dir)
        book.thumbnail_dir = thumbnail_dir

    except BookPrintAPIError as e:
        logger.error(f"확정 중 API 오류: {e.message}")
        raise HTTPException(status_code=502, detail=f"책 업로드 중 오류: {e.message}")
    finally:
        await service.close()

    book.status = "confirmed"
    db.commit()
    return {"message": "동화책이 확정되었습니다", "status": "confirmed"}
