"""동화책 스토리/이미지 생성 서비스

2단계 분리 구조:
  1단계: generate_story_only() — 스토리 텍스트만 생성 (빠름, ~10초)
  2단계: generate_illustrations() — 확정된 텍스트 기반 일러스트 생성
  + generate_cover_image() — 표지 전용 이미지 생성

기존 generate_story()는 하위 호환성을 위해 유지 (1+2단계 한번에).
"""
import logging
import os
from datetime import date, datetime, timezone
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
# → 일러스트 AI 생성을 활성화하려면 False로 변경하세요.
# ============================================================
SKIP_AI_ILLUSTRATION = True

# 더미 placeholder 색상 팔레트 (파스텔 톤)
def _calc_child_age(birth_date) -> int:
    """생년월일로 만 나이를 계산한다. 없으면 기본 6세."""
    if not birth_date:
        return 6
    today = date.today()
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return max(3, min(age, 12))  # 3~12세 범위 제한


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


def _create_placeholder_image(page_number: int, label: str, book_id: int) -> str:
    """실제 PNG 파일로 placeholder 이미지를 생성하여 uploads/ 디렉토리에 저장."""
    from PIL import Image, ImageDraw, ImageFont

    ensure_upload_dir()

    width, height = 1024, 1024
    color = PLACEHOLDER_COLORS[(page_number - 1) % len(PLACEHOLDER_COLORS)]
    img = Image.new("RGB", (width, height), color)

    draw = ImageDraw.Draw(img)
    text = f"Page {page_number}\n{label}"
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (IOError, OSError):
        font = ImageFont.load_default()

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


def _generate_single_illustration(
    book: Book,
    page_number: int,
    scene_description: str,
    text_content: str,
    character_sheet_path: Optional[str],
) -> str:
    """AI 일러스트를 시도하고, 실패하면 placeholder를 생성한다."""
    ensure_upload_dir()

    if SKIP_AI_ILLUSTRATION:
        logger.info(f"[SKIP] 일러스트 AI 생성 스킵 (p{page_number})")
        label = text_content[:30] if text_content else f"Page {page_number}"
        return _create_placeholder_image(page_number, label, book.id)

    if scene_description:
        child_age = _calc_child_age(book.child_birth_date)
        child_gender = book.child_gender or "male"
        ai_bytes = generate_illustration_or_dummy(
            character_sheet_path=character_sheet_path or "",
            scene_description=scene_description,
            art_style=book.art_style or "watercolor",
            child_name=book.child_name,
            job_name=book.job_name or "직업",
            child_age=child_age,
            child_gender=child_gender,
        )
        if ai_bytes:
            filename = f"ai_illust_book{book.id}_page{page_number}.png"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(ai_bytes)
            return filepath

    label = text_content[:30] if text_content else f"Page {page_number}"
    return _create_placeholder_image(page_number, label, book.id)


# ============================================================
# 1단계: 스토리 텍스트만 생성
# ============================================================

def generate_story_only(
    db: Session,
    book: Book,
) -> List[Page]:
    """스토리 텍스트만 생성하여 DB에 저장. 이미지는 생성하지 않음.

    24페이지 구조:
      p1: 제목 (title) — 텍스트만
      p2: 그림1 (illustration) — 텍스트 없음, 이미지 없음
      p3: 이야기1 (story) — 텍스트만
      ...
      p22: 그림11 (illustration)
      p23: 이야기11 (story)
      p24: 판권 (colophon)

    이 함수 후 사용자가 텍스트를 편집하고,
    그 다음 generate_illustrations()를 호출하여 이미지를 생성한다.
    """
    child_name = book.child_name
    job_name = book.job_name or "직업"
    art_style = book.art_style
    plot_input = book.plot_input or ""
    child_age = _calc_child_age(book.child_birth_date)
    child_gender = book.child_gender or "male"

    # AI 또는 더미 스토리 생성
    story_data = generate_story_with_gpt_or_dummy(
        child_name=child_name,
        job_name=job_name,
        plot_input=plot_input,
        art_style=art_style,
        child_age=child_age,
        child_gender=child_gender,
    )

    # 기존 페이지 삭제 (재생성 시)
    db.query(Page).filter(Page.book_id == book.id).delete()
    db.flush()

    pages = []
    now = datetime.now(timezone.utc)
    title = story_data.get("title", f"{child_name}의 꿈 — 멋진 {job_name}")
    stories = story_data.get("stories", [])

    # p1: 제목 페이지
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
    pages.append(title_page)

    # p2~p23: [그림+이야기] × 11
    for i, entry in enumerate(stories[:STORY_PAGE_COUNT]):
        illust_page_num = 2 + i * 2      # 2, 4, 6, ..., 22
        text_page_num = 3 + i * 2        # 3, 5, 7, ..., 23

        scene_desc = entry.get("scene_description", "")
        text_content = entry.get("text", "")

        # 그림 페이지 (짝수) — 이미지 없이 scene_description만 저장
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
        pages.append(illust_page)

        # 이야기 페이지 (홀수) — 텍스트만
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
        pages.append(story_page)

    # p24: 판권 페이지
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
    pages.append(colophon_page)

    # 책 상태 업데이트 — "story_generated" (스토리만 완료, 이미지 대기)
    book.status = "story_generated"
    book.title = title
    book.page_count = TOTAL_BOOK_PAGES
    book.updated_at = now

    db.commit()

    for page in pages:
        db.refresh(page)

    logger.info(f"[generate] 스토리 텍스트 생성 완료: {len(pages)}페이지")
    return pages


# ============================================================
# 2단계: 일러스트 생성 (확정된 텍스트 기반)
# ============================================================

def generate_illustrations(
    db: Session,
    book: Book,
) -> List[Page]:
    """확정된 스토리 텍스트를 기반으로 일러스트를 생성한다.

    illustration 타입 페이지 + title 페이지에 이미지를 생성/연결한다.
    story 페이지에도 같은 이미지를 참조로 연결한다.
    """
    character_sheet_path = _get_selected_character_sheet_path(db, book.id)
    now = datetime.now(timezone.utc)

    pages = db.query(Page).filter(Page.book_id == book.id).order_by(Page.page_number).all()

    # illustration 페이지와 대응하는 story 페이지를 매칭
    illust_pages = [p for p in pages if p.page_type == "illustration"]
    story_pages = [p for p in pages if p.page_type == "story"]

    generated_count = 0

    for i, illust_page in enumerate(illust_pages):
        # 대응하는 스토리 페이지의 텍스트를 참조
        story_text = story_pages[i].text_content if i < len(story_pages) else ""
        scene_desc = illust_page.scene_description or ""

        # AI 일러스트 생성
        image_path = _generate_single_illustration(
            book=book,
            page_number=illust_page.page_number,
            scene_description=scene_desc,
            text_content=story_text,
            character_sheet_path=character_sheet_path,
        )

        # 기존 이미지 삭제 후 새로 추가
        db.query(PageImage).filter(PageImage.page_id == illust_page.id).delete()
        db.add(PageImage(
            page_id=illust_page.id,
            image_path=image_path,
            generation_index=0,
            is_selected=True,
            created_at=now,
        ))

        # 대응하는 스토리 페이지에도 같은 이미지 참조
        if i < len(story_pages):
            db.query(PageImage).filter(PageImage.page_id == story_pages[i].id).delete()
            db.add(PageImage(
                page_id=story_pages[i].id,
                image_path=image_path,
                generation_index=0,
                is_selected=True,
                created_at=now,
            ))

        generated_count += 1
        logger.info(f"[generate] 일러스트 {generated_count}/{len(illust_pages)} (p{illust_page.page_number}) 완료")

    # 제목 페이지 이미지 — 첫 일러스트 재사용
    title_page = next((p for p in pages if p.page_type == "title"), None)
    if title_page and illust_pages:
        first_illust_image = db.query(PageImage).filter(
            PageImage.page_id == illust_pages[0].id,
            PageImage.is_selected == True,
        ).first()
        if first_illust_image:
            db.query(PageImage).filter(PageImage.page_id == title_page.id).delete()
            db.add(PageImage(
                page_id=title_page.id,
                image_path=first_illust_image.image_path,
                generation_index=0,
                is_selected=True,
                created_at=now,
            ))

    # 판권 페이지 — placeholder
    colophon_page = next((p for p in pages if p.page_type == "colophon"), None)
    if colophon_page:
        existing = db.query(PageImage).filter(PageImage.page_id == colophon_page.id).first()
        if not existing:
            colophon_image = _create_placeholder_image(TOTAL_BOOK_PAGES, "판권", book.id)
            db.add(PageImage(
                page_id=colophon_page.id,
                image_path=colophon_image,
                generation_index=0,
                is_selected=True,
                created_at=now,
            ))

    # 책 상태 업데이트
    book.status = "editing"
    book.current_step = 6
    book.updated_at = now

    db.commit()

    for page in pages:
        db.refresh(page)

    logger.info(f"[generate] 일러스트 생성 완료: {generated_count}장")
    return pages


# ============================================================
# 표지 이미지 생성
# ============================================================

def generate_cover_image(
    db: Session,
    book: Book,
) -> Optional[str]:
    """표지 전용 이미지를 생성한다.

    첫 번째 일러스트의 scene_description을 기반으로
    표지에 적합한 이미지를 생성한다.

    Returns:
        생성된 이미지 파일 경로 (또는 None)
    """
    character_sheet_path = _get_selected_character_sheet_path(db, book.id)

    # 첫 번째 illustration 페이지의 scene을 표지용으로 사용
    first_illust = db.query(Page).filter(
        Page.book_id == book.id,
        Page.page_type == "illustration",
    ).order_by(Page.page_number).first()

    scene_desc = first_illust.scene_description if first_illust else ""

    if not scene_desc:
        # scene이 없으면 기본 표지 scene 생성
        scene_desc = (
            f"A cheerful child (age 6) dressed as a {book.job_name or 'professional'}, "
            f"standing confidently with a warm smile. "
            f"Background: colorful and inviting, suitable for a children's book cover."
        )

    image_path = _generate_single_illustration(
        book=book,
        page_number=0,  # 표지는 page 0
        scene_description=scene_desc,
        text_content=book.title or "",
        character_sheet_path=character_sheet_path,
    )

    logger.info(f"[generate] 표지 이미지 생성 완료: {image_path}")
    return image_path


# ============================================================
# 하위 호환: 한번에 생성 (1+2단계)
# ============================================================

def generate_story(
    db: Session,
    book: Book,
) -> List[Page]:
    """스토리 + 일러스트를 한번에 생성 (기존 호환성 유지)."""
    pages = generate_story_only(db, book)
    pages = generate_illustrations(db, book)
    return pages


# 하위 호환성
generate_dummy_story = generate_story
