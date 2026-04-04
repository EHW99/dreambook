"""AI 스토리 생성 서비스 (GPT-4o)

OpenAI GPT-4o를 사용하여 동화 스토리를 생성한다.
OPENAI_API_KEY가 없으면 더미 스토리로 폴백한다.
"""
import json
import logging
from typing import Optional

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


class StoryGenerationError(Exception):
    """스토리 생성 실패 시 발생하는 예외"""
    pass


# ──────────────────────────────────────────────
# 그림체 스타일 매핑
# ──────────────────────────────────────────────
ART_STYLE_KEYWORDS = {
    "watercolor": "watercolor illustration, soft warm tones, gentle brushstrokes",
    "pencil": "pencil sketch, hand-drawn, fine line art",
    "crayon": "crayon drawing, childlike texture, bold colors",
    "3d": "3D render, Pixar style, soft lighting, rounded shapes",
    "cartoon": "cartoon style, cel-shaded, vibrant colors, clean outlines",
}


def _build_system_prompt(story_style: str, art_style: Optional[str] = None) -> str:
    """시스템 프롬프트 구성"""
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "")

    base = """당신은 5~7세 아동용 동화 작가입니다.

## 필수 규칙
- 타겟 연령: 5~7세. 해당 연령이 이해할 수 있는 쉬운 어휘만 사용하세요.
- 아이의 이름이 주인공에 자연스럽게 반영되어야 합니다.
- 선택한 직업의 실제 활동을 구체적으로 묘사하세요 (교육적 가치).
- 각 페이지는 하나의 장면 — 일러스트로 그릴 수 있는 구체적 상황이어야 합니다.
- 기승전결 구조를 갖추세요.

## 금지 사항
- 폭력, 공포, 부정적 결말 금지
- 성인 수준의 어휘나 개념 금지
- 비현실적인 직업 묘사 금지 (소방관이 불을 마법으로 끄는 등)
- 성별/인종 고정관념 금지

## 출력 형식
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트를 추가하지 마세요.
```json
{
  "title": "동화책 제목",
  "pages": [
    {
      "page": 1,
      "page_type": "title",
      "text": "제목 페이지 텍스트",
      "scene_description": "이미지 생성을 위한 영어 장면 묘사"
    },
    {
      "page": 2,
      "page_type": "content",
      "text": "본문 텍스트",
      "scene_description": "이미지 생성을 위한 영어 장면 묘사"
    },
    ...
    {
      "page": N,
      "page_type": "ending",
      "text": "엔딩 텍스트",
      "scene_description": "이미지 생성을 위한 영어 장면 묘사"
    }
  ]
}
```

## scene_description 규칙
- scene_description은 영어로 작성하세요 (이미지 생성 AI에 전달됨).
- 캐릭터의 외형, 표정, 동작, 배경을 구체적으로 묘사하세요.
- 텍스트 배치 영역(상단 또는 하단)을 고려한 구도를 명시하세요."""

    if art_keywords:
        base += f"\n- 그림체 스타일: {art_keywords}"

    if story_style == "dreaming_today":
        base += """

## 동화 스타일: 꿈꾸는 오늘
- "어느 날, [직업]이 된 [아이이름]는..." 형식으로 시작
- 시간이나 나이를 언급하지 마세요
- 꿈이 이루어진 세계 설정
- 아이 모습 그대로 직업 활동을 하는 내용"""
    elif story_style == "future_me":
        base += """

## 동화 스타일: 미래의 나
- 성장 과정을 단계별로 묘사하세요
- 생년월일이 제공되면 미래 연도를 계산하여 활용하세요
- 일대기 구조로 작성하세요
- 아이 → 청소년 → 성인으로 성장하는 모습"""

    return base


def _build_user_prompt(
    child_name: str,
    job_name: str,
    story_style: str,
    plot_input: str,
    page_count: int,
    child_birth_date: Optional[str] = None,
) -> str:
    """사용자 프롬프트 구성"""
    prompt = f"""다음 정보로 동화 스토리를 만들어주세요.

- 아이 이름: {child_name}
- 직업: {job_name}
- 동화 스타일: {"꿈꾸는 오늘" if story_style == "dreaming_today" else "미래의 나"}
- 총 페이지 수: {page_count}페이지 (title 1페이지 + content {page_count - 2}페이지 + ending 1페이지)"""

    if child_birth_date and story_style == "future_me":
        prompt += f"\n- 생년월일: {child_birth_date}"

    if plot_input and plot_input.strip():
        prompt += f"\n- 사용자 줄거리: {plot_input}"

    prompt += f"""

정확히 {page_count}개의 페이지를 생성해주세요.
첫 번째 페이지는 page_type이 "title", 마지막 페이지는 "ending", 나머지는 "content"입니다.
JSON 형식으로만 응답해주세요."""

    return prompt


def generate_story_with_gpt(
    child_name: str,
    job_name: str,
    story_style: str,
    plot_input: str,
    page_count: int,
    art_style: Optional[str] = None,
    child_birth_date: Optional[str] = None,
) -> dict:
    """GPT-4o를 사용하여 동화 스토리를 생성한다.

    Returns:
        {"title": str, "pages": [{"page": int, "page_type": str, "text": str, "scene_description": str}, ...]}

    Raises:
        StoryGenerationError: API 호출 실패 또는 응답 파싱 실패 시
    """
    settings = get_settings()

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        system_prompt = _build_system_prompt(story_style, art_style)
        user_prompt = _build_user_prompt(
            child_name=child_name,
            job_name=job_name,
            story_style=story_style,
            plot_input=plot_input,
            page_count=page_count,
            child_birth_date=child_birth_date,
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        # 비용 모니터링 로깅
        from app.services.cost_monitor import get_cost_monitor
        monitor = get_cost_monitor()
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_tokens", 0) if usage else (prompt_tokens + completion_tokens)
        monitor.log_story_call(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            success=True,
        )

    except StoryGenerationError:
        raise
    except Exception as e:
        # 실패 시에도 비용 모니터링 로깅
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_story_call(success=False, error=str(e))
        logger.error(f"GPT-4o API 호출 실패: {e}")
        raise StoryGenerationError(f"스토리 생성 중 오류가 발생했습니다: {e}")

    # JSON 파싱
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"GPT-4o 응답 JSON 파싱 실패: {content[:200]}")
        raise StoryGenerationError(f"스토리 생성 결과를 파싱할 수 없습니다: {e}")

    # 응답 검증
    if "pages" not in result:
        raise StoryGenerationError("스토리 생성 결과에 pages가 없습니다")

    if "title" not in result:
        # title이 없으면 첫 페이지 텍스트를 title로 사용
        result["title"] = result["pages"][0].get("text", f"{child_name}의 꿈")

    # 페이지 수 검증 — 약간의 오차는 허용하되 로그 남김
    actual_count = len(result["pages"])
    if actual_count != page_count:
        logger.warning(
            f"요청 페이지 수({page_count})와 생성 페이지 수({actual_count}) 불일치"
        )

    return result


def _generate_dummy_story_data(
    child_name: str,
    job_name: str,
    page_count: int,
) -> dict:
    """더미 스토리 데이터 생성 (API 키 없을 때 폴백)"""
    dummy_texts = [
        f"옛날 옛적에, {child_name}이라는 아이가 살았어요. {child_name}는 항상 {job_name}가 되는 꿈을 꿨답니다.",
        f"어느 날, {child_name}는 학교에서 {job_name}에 대해 배웠어요. '나도 {job_name}가 될 수 있을까?' {child_name}는 눈을 반짝였어요.",
        f"방과 후, {child_name}는 도서관에서 {job_name}에 대한 책을 찾았어요. 책 속에는 멋진 {job_name}들의 이야기가 가득했답니다.",
        f"{child_name}는 집에 돌아와 엄마에게 말했어요. '엄마, 나 커서 {job_name}가 될 거예요!' 엄마는 미소를 지었어요.",
        f"다음 날, {child_name}는 친구들에게 자신의 꿈을 이야기했어요. 친구들은 '정말 멋지다!'라고 응원해 주었어요.",
        f"{child_name}는 매일 조금씩 노력했어요. {job_name}가 되기 위해 열심히 공부하고 연습했답니다.",
        f"어느 특별한 날, {child_name}는 직업 체험 행사에 참가했어요. 진짜 {job_name}처럼 멋진 옷을 입고 활동했어요.",
        f"체험을 하면서 {child_name}는 {job_name}의 일이 얼마나 중요한지 알게 되었어요. 사람들을 돕는 일이 정말 보람차다고 느꼈어요.",
        f"{child_name}는 선생님께 칭찬을 받았어요. '넌 정말 훌륭한 {job_name}가 될 거야!' {child_name}의 마음이 뿌듯해졌어요.",
        f"그날 밤, {child_name}는 별을 바라보며 약속했어요. '나는 꼭 멋진 {job_name}가 되어서 모두를 행복하게 만들 거야!'",
    ]

    pages = []
    content_count = page_count - 2

    # Title page
    pages.append({
        "page": 1,
        "page_type": "title",
        "text": f"{child_name}의 꿈 — 멋진 {job_name}",
        "scene_description": f"A child named {child_name} wearing {job_name} outfit, smiling brightly, warm pastel background",
    })

    # Content pages
    for i in range(content_count):
        template_idx = i % len(dummy_texts)
        pages.append({
            "page": i + 2,
            "page_type": "content",
            "text": dummy_texts[template_idx],
            "scene_description": f"Scene {i + 1}: {child_name} doing {job_name} activities, warm illustration style",
        })

    # Ending page
    pages.append({
        "page": page_count,
        "page_type": "ending",
        "text": f"그리고 {child_name}는 자신의 꿈을 향해 한 걸음씩 나아갔답니다. {child_name}의 꿈은 반드시 이루어질 거예요! 끝.",
        "scene_description": f"{child_name} looking at the starry night sky, dreaming about the future, warm and peaceful scene",
    })

    return {
        "title": f"{child_name}의 꿈 — 멋진 {job_name}",
        "pages": pages,
    }


def generate_story_with_gpt_or_dummy(
    child_name: str,
    job_name: str,
    story_style: str,
    plot_input: str,
    page_count: int,
    art_style: Optional[str] = None,
    child_birth_date: Optional[str] = None,
) -> dict:
    """API 키가 있으면 GPT-4o, 없으면 더미 스토리를 반환한다.

    Returns:
        {"title": str, "pages": [{"page": int, "page_type": str, "text": str, "scene_description": str}, ...]}

    Raises:
        StoryGenerationError: API 키가 있는데 호출 실패 시
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 스토리 폴백")
        return _generate_dummy_story_data(child_name, job_name, page_count)

    return generate_story_with_gpt(
        child_name=child_name,
        job_name=job_name,
        story_style=story_style,
        plot_input=plot_input,
        page_count=page_count,
        art_style=art_style,
        child_birth_date=child_birth_date,
    )
