"""동화책 더미 스토리/이미지 생성 서비스 (Phase 2)"""
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.page import Page
from app.models.page_image import PageImage


# 더미 스토리 템플릿 (아이 이름, 직업을 치환)
DUMMY_STORY_TEMPLATES = {
    "title": "{child_name}의 꿈 — 멋진 {job_name}",
    "pages": [
        "옛날 옛적에, {child_name}이라는 아이가 살았어요. {child_name}는 항상 {job_name}가 되는 꿈을 꿨답니다.",
        "어느 날, {child_name}는 학교에서 {job_name}에 대해 배웠어요. '나도 {job_name}가 될 수 있을까?' {child_name}는 눈을 반짝였어요.",
        "방과 후, {child_name}는 도서관에서 {job_name}에 대한 책을 찾았어요. 책 속에는 멋진 {job_name}들의 이야기가 가득했답니다.",
        "{child_name}는 집에 돌아와 엄마에게 말했어요. '엄마, 나 커서 {job_name}가 될 거예요!' 엄마는 미소를 지었어요.",
        "다음 날, {child_name}는 친구들에게 자신의 꿈을 이야기했어요. 친구들은 '정말 멋지다!'라고 응원해 주었어요.",
        "{child_name}는 매일 조금씩 노력했어요. {job_name}가 되기 위해 열심히 공부하고 연습했답니다.",
        "어느 특별한 날, {child_name}는 직업 체험 행사에 참가했어요. 진짜 {job_name}처럼 멋진 옷을 입고 활동했어요.",
        "체험을 하면서 {child_name}는 {job_name}의 일이 얼마나 중요한지 알게 되었어요. 사람들을 돕는 일이 정말 보람차다고 느꼈어요.",
        "{child_name}는 선생님께 칭찬을 받았어요. '넌 정말 훌륭한 {job_name}가 될 거야!' {child_name}의 마음이 뿌듯해졌어요.",
        "그날 밤, {child_name}는 별을 바라보며 약속했어요. '나는 꼭 멋진 {job_name}가 되어서 모두를 행복하게 만들 거야!'",
    ],
    "ending": "그리고 {child_name}는 자신의 꿈을 향해 한 걸음씩 나아갔답니다. {child_name}의 꿈은 반드시 이루어질 거예요! 끝.",
}

# 더미 placeholder 이미지 경로
DUMMY_IMAGE_PATH = "/placeholder/illustration_{page_number}.png"


def generate_dummy_story(
    db: Session,
    book: Book,
) -> List[Page]:
    """더미 스토리와 이미지를 생성하여 pages + page_images 테이블에 삽입"""
    child_name = book.child_name
    job_name = book.job_name or "직업"
    page_count = book.page_count or 24

    # 내지 페이지 수 계산: page_count / 2 (양면)
    # title(1) + content(N) + ending(1)
    total_pages = page_count // 2
    content_pages = total_pages - 2  # title과 ending 제외

    # 기존 페이지 삭제 (재생성 시)
    db.query(Page).filter(Page.book_id == book.id).delete()
    db.flush()

    pages = []
    now = datetime.now(timezone.utc)

    # 1. 제목 페이지
    title_text = DUMMY_STORY_TEMPLATES["title"].format(
        child_name=child_name, job_name=job_name
    )
    title_page = Page(
        book_id=book.id,
        page_number=1,
        page_type="title",
        scene_description=f"{child_name}가 {job_name} 옷을 입고 환하게 웃고 있는 장면",
        text_content=title_text,
        created_at=now,
        updated_at=now,
    )
    db.add(title_page)
    db.flush()

    # 제목 페이지 이미지
    title_image = PageImage(
        page_id=title_page.id,
        image_path=DUMMY_IMAGE_PATH.format(page_number=1),
        generation_index=0,
        is_selected=True,
        created_at=now,
    )
    db.add(title_image)
    pages.append(title_page)

    # 2. 내용 페이지들
    story_templates = DUMMY_STORY_TEMPLATES["pages"]
    for i in range(content_pages):
        # 템플릿 반복 사용 (템플릿 수보다 페이지가 많을 경우)
        template_idx = i % len(story_templates)
        text = story_templates[template_idx].format(
            child_name=child_name, job_name=job_name
        )
        content_page = Page(
            book_id=book.id,
            page_number=i + 2,
            page_type="content",
            scene_description=f"{child_name}가 {job_name} 활동을 하는 장면 {i + 1}",
            text_content=text,
            created_at=now,
            updated_at=now,
        )
        db.add(content_page)
        db.flush()

        content_image = PageImage(
            page_id=content_page.id,
            image_path=DUMMY_IMAGE_PATH.format(page_number=i + 2),
            generation_index=0,
            is_selected=True,
            created_at=now,
        )
        db.add(content_image)
        pages.append(content_page)

    # 3. 엔딩 페이지
    ending_text = DUMMY_STORY_TEMPLATES["ending"].format(
        child_name=child_name, job_name=job_name
    )
    ending_page = Page(
        book_id=book.id,
        page_number=total_pages,
        page_type="ending",
        scene_description=f"{child_name}가 밤하늘의 별을 바라보며 꿈을 꾸는 장면",
        text_content=ending_text,
        created_at=now,
        updated_at=now,
    )
    db.add(ending_page)
    db.flush()

    ending_image = PageImage(
        page_id=ending_page.id,
        image_path=DUMMY_IMAGE_PATH.format(page_number=total_pages),
        generation_index=0,
        is_selected=True,
        created_at=now,
    )
    db.add(ending_image)
    pages.append(ending_page)

    # 책 상태 업데이트
    book.status = "editing"
    book.current_step = 9
    book.title = title_text
    book.updated_at = now

    db.commit()

    # 이미지 관계 로드를 위해 refresh
    for page in pages:
        db.refresh(page)

    return pages
