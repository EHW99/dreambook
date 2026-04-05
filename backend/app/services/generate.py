"""동화책 스토리/이미지 생성 서비스

Phase 3: GPT-4o 스토리 + GPT Image 일러스트 생성
폴백: API 키 없으면 더미 스토리 + placeholder 이미지
"""
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.page import Page
from app.models.page_image import PageImage
from app.services.photo import UPLOAD_DIR, ensure_upload_dir
from app.services.ai_story import (
    generate_story_with_gpt_or_dummy,
    StoryGenerationError,
    STORY_PAGE_COUNT,
    TOTAL_BOOK_PAGES,
)
from app.services.ai_illustration import generate_illustration_or_dummy

logger = logging.getLogger(__name__)

# ============================================================
# [AI 이미지 생성 스킵 플래그]
# True로 설정하면 일러스트 생성 시 AI(GPT Image)를 호출하지 않고
# 항상 placeholder 이미지를 사용합니다.
# 스토리(GPT-4o 텍스트)는 이 플래그와 무관하게 정상 동작합니다.
#
# → 일러스트 AI 생성을 활성화하려면 False로 변경하세요.
# ============================================================
SKIP_AI_ILLUSTRATION = True

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


def _get_selected_character_sheet_path(db: Session, book_id: int) -> Optional[str]:
    """확정된 캐릭터 시트의 이미지 경로를 반환한다."""
    from app.models.character_sheet import CharacterSheet
    selected = db.query(CharacterSheet).filter(
        CharacterSheet.book_id == book_id,
        CharacterSheet.is_selected == True,
    ).first()
    if selected:
        return selected.image_path
    return None


def _generate_page_illustration(
    book: Book,
    page_number: int,
    scene_description: str,
    text_content: str,
    character_sheet_path: Optional[str],
) -> str:
    """AI 일러스트를 시도하고, 실패하면 placeholder를 생성한다.

    Returns:
        저장된 이미지의 파일 경로
    """
    ensure_upload_dir()

    # ── SKIP_AI_ILLUSTRATION=True이면 AI 호출 없이 placeholder 사용 ──
    if SKIP_AI_ILLUSTRATION:
        logger.info(f"[SKIP] 일러스트 AI 생성 스킵 (p{page_number}) — SKIP_AI_ILLUSTRATION=True")
        label = text_content[:30] if text_content else f"Page {page_number}"
        return _create_placeholder_image(page_number, label, book.id)

    # 캐릭터 시트가 있고 scene_description이 있으면 AI 일러스트 시도
    if character_sheet_path and scene_description and os.path.exists(character_sheet_path):
        ai_bytes = generate_illustration_or_dummy(
            character_sheet_path=character_sheet_path,
            scene_description=scene_description,
            art_style=book.art_style or "watercolor",
            child_name=book.child_name,
            job_name=book.job_name or "직업",
        )

        if ai_bytes:
            filename = f"ai_illust_book{book.id}_page{page_number}.png"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(ai_bytes)
            return filepath
    else:
        if scene_description:
            ai_bytes = generate_illustration_or_dummy(
                character_sheet_path=character_sheet_path or "",
                scene_description=scene_description,
                art_style=book.art_style or "watercolor",
                child_name=book.child_name,
                job_name=book.job_name or "직업",
            )
            if ai_bytes:
                filename = f"ai_illust_book{book.id}_page{page_number}.png"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(ai_bytes)
                return filepath

    # 폴백: placeholder 이미지
    label = text_content[:30] if text_content else f"Page {page_number}"
    return _create_placeholder_image(page_number, label, book.id)


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

    24페이지 고정 구성:
      p1: 제목 페이지 (title)
      p2: 그림1, p3: 이야기1
      p4: 그림2, p5: 이야기2
      ...
      p22: 그림11, p23: 이야기11
      p24: 판권 (colophon)

    LLM이 생성한 stories(11개)를 위 구조로 펼친다.
    그림 페이지(짝수)에만 AI 일러스트를 생성한다.

    Raises:
        StoryGenerationError: AI 스토리 생성 실패 시
    """
    child_name = book.child_name
    job_name = book.job_name or "직업"
    art_style = book.art_style
    plot_input = book.plot_input or ""

    # AI 또는 더미 스토리 생성 (이야기 11개)
    story_data = generate_story_with_gpt_or_dummy(
        child_name=child_name,
        job_name=job_name,
        plot_input=plot_input,
        art_style=art_style,
    )

    # 기존 페이지 삭제 (재생성 시)
    db.query(Page).filter(Page.book_id == book.id).delete()
    db.flush()

    # 확정된 캐릭터 시트 경로 조회
    character_sheet_path = _get_selected_character_sheet_path(db, book.id)

    pages = []
    now = datetime.now(timezone.utc)
    title = story_data.get("title", f"{child_name}의 꿈 — 멋진 {job_name}")
    stories = story_data.get("stories", [])

    # ── p1: 제목 페이지 ──
    title_page = Page(
        book_id=book.id,
        page_number=1,
        page_type="title",
        scene_description="",
        text_content=title,
        created_at=now,
        updated_at=now,
    )
    db.add(title_page)
    db.flush()

    # 제목 페이지 이미지: 첫 번째 이야기의 scene_description 활용
    first_scene = stories[0]["scene_description"] if stories else ""
    title_image_path = _generate_page_illustration(
        book=book,
        page_number=1,
        scene_description=first_scene,
        text_content=title,
        character_sheet_path=character_sheet_path,
    )
    db.add(PageImage(
        page_id=title_page.id,
        image_path=title_image_path,
        generation_index=0,
        is_selected=True,
        created_at=now,
    ))
    pages.append(title_page)
    logger.info(f"페이지 1/{TOTAL_BOOK_PAGES} (제목) 완료")

    # ── p2~p23: [그림+이야기] × 11 ──
    for i, entry in enumerate(stories[:STORY_PAGE_COUNT]):
        story_num = i + 1
        illust_page_num = 2 + i * 2      # 2, 4, 6, ..., 22
        text_page_num = 3 + i * 2        # 3, 5, 7, ..., 23

        scene_desc = entry.get("scene_description", "")
        text_content = entry.get("text", "")

        # 그림 페이지 (짝수)
        illust_page = Page(
            book_id=book.id,
            page_number=illust_page_num,
            page_type="illustration",
            scene_description=scene_desc,
            text_content="",
            created_at=now,
            updated_at=now,
        )
        db.add(illust_page)
        db.flush()

        image_path = _generate_page_illustration(
            book=book,
            page_number=illust_page_num,
            scene_description=scene_desc,
            text_content=text_content,
            character_sheet_path=character_sheet_path,
        )
        db.add(PageImage(
            page_id=illust_page.id,
            image_path=image_path,
            generation_index=0,
            is_selected=True,
            created_at=now,
        ))
        pages.append(illust_page)

        # 이야기 페이지 (홀수)
        story_page = Page(
            book_id=book.id,
            page_number=text_page_num,
            page_type="story",
            scene_description=scene_desc,
            text_content=text_content,
            created_at=now,
            updated_at=now,
        )
        db.add(story_page)
        db.flush()

        # 이야기 페이지에도 같은 일러스트를 참조 (편집 시 배경으로 사용 가능)
        db.add(PageImage(
            page_id=story_page.id,
            image_path=image_path,
            generation_index=0,
            is_selected=True,
            created_at=now,
        ))
        pages.append(story_page)

        logger.info(f"이야기 {story_num}/{STORY_PAGE_COUNT} (p{illust_page_num}-{text_page_num}) 완료")

    # ── p24: 판권 페이지 ──
    colophon_text = f"{title}\n\n지은이: {child_name}\n제작: AI 동화책 서비스 Dreambook"
    colophon_page = Page(
        book_id=book.id,
        page_number=TOTAL_BOOK_PAGES,
        page_type="colophon",
        scene_description="",
        text_content=colophon_text,
        created_at=now,
        updated_at=now,
    )
    db.add(colophon_page)
    db.flush()

    colophon_image_path = _create_placeholder_image(TOTAL_BOOK_PAGES, "판권", book.id)
    db.add(PageImage(
        page_id=colophon_page.id,
        image_path=colophon_image_path,
        generation_index=0,
        is_selected=True,
        created_at=now,
    ))
    pages.append(colophon_page)
    logger.info(f"페이지 {TOTAL_BOOK_PAGES}/{TOTAL_BOOK_PAGES} (판권) 완료")

    # 책 상태 업데이트
    book.status = "editing"
    book.current_step = 6
    book.title = title
    book.page_count = TOTAL_BOOK_PAGES
    book.updated_at = now

    db.commit()

    for page in pages:
        db.refresh(page)

    return pages


# 하위 호환성
generate_dummy_story = generate_story
