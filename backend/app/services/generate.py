"""동화책 스토리/이미지 생성 서비스

Phase 3: GPT-4o를 사용한 AI 스토리 생성 (OPENAI_API_KEY 필요)
폴백: API 키 없으면 더미 스토리 반환
"""
import logging
import os
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.page import Page
from app.models.page_image import PageImage
from app.services.photo import UPLOAD_DIR, ensure_upload_dir
from app.services.ai_story import (
    generate_story_with_gpt_or_dummy,
    StoryGenerationError,
)

logger = logging.getLogger(__name__)

# 더미 placeholder 색상 팔레트 (파스텔 톤)
PLACEHOLDER_COLORS = [
    (255, 218, 185),  # peach
    (173, 216, 230),  # light blue
    (221, 160, 221),  # plum
    (144, 238, 144),  # light green
    (255, 255, 186),  # light yellow
    (255, 182, 193),  # light pink
    (176, 224, 230),  # powder blue
    (216, 191, 216),  # thistle
    (240, 230, 140),  # khaki
    (152, 251, 152),  # pale green
    (255, 228, 196),  # bisque
    (175, 238, 238),  # pale turquoise
]


def _create_placeholder_image(page_number: int, label: str, book_id: int) -> str:
    """실제 PNG 파일로 placeholder 이미지를 생성하여 uploads/ 디렉토리에 저장.

    Returns:
        생성된 이미지의 절대 경로
    """
    from PIL import Image, ImageDraw, ImageFont

    ensure_upload_dir()

    width, height = 800, 800
    color = PLACEHOLDER_COLORS[(page_number - 1) % len(PLACEHOLDER_COLORS)]
    img = Image.new("RGB", (width, height), color)

    draw = ImageDraw.Draw(img)
    # 간단한 텍스트 표기 (폰트가 없어도 기본 폰트 사용)
    text = f"Page {page_number}\n{label}"
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (IOError, OSError):
        font = ImageFont.load_default()

    # 텍스트를 중앙에 배치
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = (height - text_h) // 2
    draw.text((x, y), text, fill=(80, 80, 80), font=font)

    filename = f"placeholder_book{book_id}_page{page_number}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)
    img.save(filepath, "PNG")

    return filepath


def generate_story(
    db: Session,
    book: Book,
) -> List[Page]:
    """AI 또는 더미 스토리를 생성하여 pages + page_images 테이블에 삽입.

    OPENAI_API_KEY가 설정되어 있으면 GPT-4o를 사용하고,
    없으면 더미 스토리로 폴백한다.

    Raises:
        StoryGenerationError: AI 스토리 생성 실패 시
    """
    child_name = book.child_name
    job_name = book.job_name or "직업"
    page_count = book.page_count or 24
    story_style = book.story_style or "dreaming_today"
    art_style = book.art_style
    plot_input = book.plot_input or ""
    child_birth_date = None
    if book.child_birth_date:
        child_birth_date = str(book.child_birth_date)

    # AI 또는 더미 스토리 생성
    story_data = generate_story_with_gpt_or_dummy(
        child_name=child_name,
        job_name=job_name,
        story_style=story_style,
        plot_input=plot_input,
        page_count=page_count,
        art_style=art_style,
        child_birth_date=child_birth_date,
    )

    # 기존 페이지 삭제 (재생성 시)
    db.query(Page).filter(Page.book_id == book.id).delete()
    db.flush()

    pages = []
    now = datetime.now(timezone.utc)

    for page_data in story_data["pages"]:
        page_number = page_data["page"]
        page_type = page_data.get("page_type", "content")
        text_content = page_data["text"]
        scene_description = page_data.get("scene_description", "")

        page = Page(
            book_id=book.id,
            page_number=page_number,
            page_type=page_type,
            scene_description=scene_description,
            text_content=text_content,
            created_at=now,
            updated_at=now,
        )
        db.add(page)
        db.flush()

        # placeholder 이미지 생성
        label = text_content[:30] if text_content else f"Page {page_number}"
        image_path = _create_placeholder_image(page_number, label, book.id)
        image = PageImage(
            page_id=page.id,
            image_path=image_path,
            generation_index=0,
            is_selected=True,
            created_at=now,
        )
        db.add(image)
        pages.append(page)

    # 책 상태 업데이트
    book.status = "editing"
    book.current_step = 9
    book.title = story_data.get("title", f"{child_name}의 꿈 — 멋진 {job_name}")
    book.updated_at = now

    db.commit()

    # 이미지 관계 로드를 위해 refresh
    for page in pages:
        db.refresh(page)

    return pages


# 하위 호환성: 기존 코드에서 generate_dummy_story를 호출하는 경우를 위한 별칭
generate_dummy_story = generate_story
