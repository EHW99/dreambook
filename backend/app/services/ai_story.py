"""AI 스토리 생성 서비스 (GPT-4o-mini)

OpenAI GPT-4o-mini를 사용하여 동화 스토리를 생성한다.
24페이지 고정 구성: 제목(1p) + [그림+이야기]×11(2~23p) + 판권(24p)
LLM은 이야기 텍스트 11개를 생성한다. scene_description은 별도 단계에서 생성.
OPENAI_API_KEY가 없으면 더미 스토리로 폴백한다.
"""
import json
import logging
from typing import Optional, Literal

from openai import OpenAI
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

# 고정 상수
STORY_PAGE_COUNT = 11  # 이야기 개수 (= 일러스트 개수)
TOTAL_BOOK_PAGES = 24  # 총 페이지 수


class StoryGenerationError(Exception):
    """스토리 생성 실패 시 발생하는 예외"""
    pass


# ──────────────────────────────────────────────
# Structured Outputs 스키마
# ──────────────────────────────────────────────
class StoryEntry(BaseModel):
    story_number: int
    text: str


class StoryOutput(BaseModel):
    title: str
    stories: list[StoryEntry]


# ──────────────────────────────────────────────
# 그림체 스타일 매핑
# ──────────────────────────────────────────────
ART_STYLE_KEYWORDS = {
    "watercolor": "watercolor illustration, soft warm tones, gentle brushstrokes",
    "pastel": "soft pastel illustration, dreamy muted tones, gentle chalky texture",
    "crayon": "crayon drawing, childlike texture, bold colors",
    "3d": "3D render, Pixar style, soft lighting, rounded shapes",
    "cartoon": "cartoon style, cel-shaded, vibrant colors, clean outlines",
}


# ──────────────────────────────────────────────
# Few-shot 예시 — 3개 직업 (소방관, 의사, 요리사)
# 각 직업마다 이야기 1(도입), 10(절정 직후), 11(결말)
# 톤, 분량(3~4문장), 현실감, 오감 묘사, 감정선의 기준을 보여준다
# ──────────────────────────────────────────────
FEW_SHOT_FIREFIGHTER = """{
  "title": "소방관 하준이의 뜨거운 하루",
  "stories": [
    {
      "story_number": 1,
      "text": "소방서에 출동 벨이 울리자 하준이는 방화복을 입고 헬멧을 눌러 썼어요. 묵직한 장비를 어깨에 메고 소방차에 올라타니, 사이렌 소리와 함께 차가 힘차게 달리기 시작했어요. 창밖으로 스쳐 지나가는 거리를 바라보며 하준이는 장갑 끈을 꽉 조였어요. 어디선가 하준이를 기다리는 사람이 있을 테니까요."
    },
    {
      "story_number": 10,
      "text": "마지막 불꽃까지 꺼지자, 시커먼 연기 사이로 파란 하늘이 보이기 시작했어요. 건물 밖에서 기다리던 할머니가 하준이의 그을린 손을 꼭 잡으며 '고맙다, 고마워' 하고 말씀하셨어요. 할머니의 따뜻한 눈물이 하준이 손등 위로 떨어졌어요. 뜨거운 불보다 더 뜨거운 것이 가슴속에서 퍼져 나갔답니다."
    },
    {
      "story_number": 11,
      "text": "소방서 옥상에 올라서니 저녁노을이 온 마을을 주황빛으로 물들이고 있었어요. 여기저기 하나둘 켜지는 불빛이 오늘 지켜낸 사람들의 저녁 식탁 같았어요. 하준이는 까맣게 그을린 장갑을 가만히 내려다보며 중얼거렸어요. '내일도 이 마을의 불빛을 지키는 사람이 되어야지.'"
    }
  ]
}"""

FEW_SHOT_DOCTOR = """{
  "title": "의사 수아의 특별한 하루",
  "stories": [
    {
      "story_number": 1,
      "text": "하얀 가운을 입고 청진기를 목에 건 수아가 병원 복도를 걸어갔어요. 간호사가 '수아 선생님, 오늘 첫 환자가 오셨어요' 하고 알려주었어요. 진료실 문을 열자 겁먹은 표정의 아이가 엄마 뒤에 숨어 있었어요. 수아는 아이의 눈높이에 맞춰 앉으며 다정하게 미소를 지었답니다."
    },
    {
      "story_number": 10,
      "text": "며칠 동안 열이 내리지 않던 아이의 체온이 드디어 정상으로 돌아왔어요. 수아가 '다 나았어요, 이제 괜찮아요' 하고 말하자 아이가 이불 속에서 고개를 내밀며 환하게 웃었어요. 옆에 있던 엄마가 수아의 손을 꼭 잡으며 고개를 숙였어요. 수아도 모르게 코끝이 찡해졌답니다."
    },
    {
      "story_number": 11,
      "text": "환자가 모두 돌아간 텅 빈 진료실에 노을빛이 길게 내려앉았어요. 수아는 오늘 만났던 환자들의 얼굴을 하나하나 떠올리며 청진기를 가운 위에 올려놓았어요. 창밖에 별 하나가 반짝이자, 수아는 조용히 속삭였어요. '내일도 이 자리에서 한 사람 한 사람, 꼭 낫게 해 줄 거야.'"
    }
  ]
}"""

FEW_SHOT_CHEF = """{
  "title": "요리사 지우의 맛있는 도전",
  "stories": [
    {
      "story_number": 1,
      "text": "새벽 시장에서 막 도착한 채소 상자를 열자, 싱싱한 풀 내음이 주방 가득 퍼졌어요. 지우는 잘 익은 토마토를 손바닥 위에 올리고 꾹 눌러 보았어요. '좋아, 오늘 재료는 최고야.' 도마 위에 칼을 가지런히 놓고 앞치마 끈을 단단히 묶자 긴 하루가 시작되었답니다."
    },
    {
      "story_number": 10,
      "text": "마지막 접시 위에 허브 잎 하나를 올려놓는 순간, 홀에서 박수 소리가 들려왔어요. 손님이 주방 쪽을 향해 엄지를 치켜세우고 있었어요. 접시 위에는 국물 한 방울도 남아 있지 않았어요. 지우는 이마의 땀을 훔치며 생각했어요. 오늘 흘린 땀이 하나도 아깝지 않다고."
    },
    {
      "story_number": 11,
      "text": "손님이 모두 떠난 조용한 주방에서 지우는 도마와 칼을 정성껏 닦았어요. 환풍기 소리만 울리는 주방에 고소한 볶음 요리의 잔향이 아직 남아 있었어요. 깨끗해진 조리대에 내일의 메뉴 메모를 붙이며, 지우는 혼잣말했어요. '내일은 오늘보다 더 맛있게 만들어 볼 거야.'"
    }
  ]
}"""


def _gender_ko(gender: str) -> str:
    """성별 한국어 변환"""
    return "남자아이" if gender == "male" else "여자아이"


def _gender_en(gender: str) -> str:
    """성별 영어 변환"""
    return "boy" if gender == "male" else "girl"


def _build_system_prompt(
    art_style: Optional[str] = None,
    child_age: int = 6,
    child_gender: str = "male",
) -> str:
    """시스템 프롬프트 구성"""
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "")
    gender_ko = _gender_ko(child_gender)
    gender_en = _gender_en(child_gender)

    base = f"""당신은 아동용 동화 작가입니다.

## 책 구성
24페이지 동화책을 위해 정확히 11개의 이야기를 만들어주세요.
책 구성: 제목(1p) + [그림+이야기]×11 (2~23p) + 판권(24p)
당신이 만들 것: title(책 제목) + stories(이야기 11개)

## 주인공 정보
- 주인공은 {child_age}세 {gender_ko}입니다.

## 세계관
- 아이가 이미 그 직업인 세계입니다. 꿈이 아니라 현실입니다.
- "꿈을 꿨어요", "눈을 떠 보니", "~가 되고 싶어요" 같은 표현은 절대 금지합니다.
- 아이는 이미 그 직업으로 일하고 있으며, 자연스러운 하루를 보냅니다.
- 시간이나 나이를 언급하지 마세요.
- 아이 모습({child_age}세 {gender_ko}) 그대로 직업 활동을 능숙하게 수행합니다.

## 필수 규칙
- 타겟 연령: 5~7세. 해당 연령이 이해할 수 있는 쉬운 어휘만 사용하세요.
- 아이의 이름이 주인공에 자연스럽게 반영되어야 합니다.
- 선택한 직업의 실제 활동을 구체적으로 묘사하세요 (교육적 가치).
- 각 이야기는 3~4문장이며, 하나의 장면을 생생하게 묘사합니다.
- 이야기 1(도입)은 아이가 자신의 직업으로 하루를 시작하는 활기찬 모습을 담으세요.
- 이야기 11(결말)은 보람찬 하루를 돌아보며 따뜻한 다짐과 여운을 남기세요.
- 전체 11개 이야기가 기승전결 구조를 갖추세요:
  - 이야기 1~3: 도입 (상황 설정, 첫 경험의 설렘)
  - 이야기 4~7: 전개 (직업 활동, 사건 발생, 배움)
  - 이야기 8~10: 절정 (도전과 해결, 성취감)
  - 이야기 11: 결말 (따뜻한 여운, 내일에 대한 다짐)

## 현실감 규칙
- 모든 사건은 해당 직업의 현장에서 실제로 벌어지는 활동이어야 합니다.
- 직업인이 매일 하는 구체적인 업무 과정을 묘사하세요 (도구 사용, 절차, 협업 등).
- 이야기 흐름과 관련 없는 돌발 사건을 끼워 넣지 마세요. 모든 장면이 하나의 줄거리 안에서 자연스럽게 연결되어야 합니다.
- 소리, 냄새, 촉감, 온도 같은 오감 묘사를 포함하여 현장감을 살리세요.
- 감정선을 풍부하게 — 긴장, 설렘, 집중, 뿌듯함 등 장면마다 주인공의 감정이 드러나야 합니다.

## 줄거리 준수
- 사용자가 제공한 줄거리 방향이 있다면, 반드시 그 줄거리를 중심으로 11개 이야기를 전개하세요.
- 줄거리에 나온 핵심 사건과 상황이 이야기 속에 자연스럽게 녹아들어야 합니다.
- 줄거리를 임의로 바꾸거나 무시하지 마세요.

## 금지 사항
- 폭력, 공포, 부정적 결말 금지
- 성인 수준의 어휘나 개념 금지
- 비현실적인 직업 묘사 금지 (소방관이 불을 마법으로 끄는 등)
- 성별/인종 고정관념 금지

## 출력 형식
- title: 책 제목
- stories: 11개의 이야기 (story_number 1~11, text만 포함)"""

    if art_keywords:
        base += f"\n- 그림체 스타일: {art_keywords}"

    return base


def _build_user_prompt(
    child_name: str,
    job_name: str,
    plot_input: str,
) -> str:
    """사용자 프롬프트 구성 (Few-shot 포함)"""
    prompt = f"""## 예시 (3개 직업)
다음은 소방관, 의사, 요리사 동화의 이야기 1(도입), 10(절정 직후), 11(결말) 예시입니다.
현실감 있는 직업 묘사, 오감 표현, 감정선의 수준을 참고하세요:

### 소방관 예시
{FEW_SHOT_FIREFIGHTER}

### 의사 예시
{FEW_SHOT_DOCTOR}

### 요리사 예시
{FEW_SHOT_CHEF}

---

## 실제 요청
다음 정보로 동화 스토리를 만들어주세요.

- 아이 이름: {child_name}
- 직업: {job_name}"""

    if plot_input and plot_input.strip():
        prompt += f"""

## 줄거리 (반드시 따라야 합니다)
{plot_input}

위 줄거리의 핵심 사건과 흐름을 기반으로 11개 이야기를 전개하세요.
줄거리에 나온 상황이 이야기 속에 자연스럽게 포함되어야 합니다."""

    prompt += """

정확히 11개의 이야기(story_number 1~11)를 생성해주세요.
각 이야기의 text는 한국어 3~4문장으로 장면을 생생하게 묘사해주세요.
특히 이야기 1(도입)과 이야기 11(결말)에 공을 들여주세요."""

    return prompt


def generate_story_with_gpt(
    child_name: str,
    job_name: str,
    plot_input: str,
    art_style: Optional[str] = None,
    child_age: int = 6,
    child_gender: str = "male",
) -> dict:
    """GPT-4o를 사용하여 동화 스토리를 생성한다.

    Returns:
        {"title": str, "stories": [{"story_number": int, "text": str}, ...]}

    Raises:
        StoryGenerationError: API 호출 실패 시
    """
    settings = get_settings()

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        system_prompt = _build_system_prompt(art_style, child_age, child_gender)
        user_prompt = _build_user_prompt(
            child_name=child_name,
            job_name=job_name,
            plot_input=plot_input,
        )
        logger.info(f"[ai_story] 생성 요청: {child_name}, {job_name}, {child_age}세, {child_gender}")

        response = client.beta.chat.completions.parse(
            model=settings.TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=4096,
            response_format=StoryOutput,
        )

        parsed = response.choices[0].message.parsed

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
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_story_call(success=False, error=str(e))
        logger.error(f"GPT-4o API 호출 실패: {e}")
        raise StoryGenerationError(f"스토리 생성 중 오류가 발생했습니다: {e}")

    if parsed is None:
        raise StoryGenerationError("스토리 생성 결과가 비어 있습니다 (refusal)")

    result = parsed.model_dump()

    # 이야기 개수 검증
    actual_count = len(result["stories"])
    if actual_count != STORY_PAGE_COUNT:
        logger.warning(
            f"요청 이야기 수({STORY_PAGE_COUNT})와 생성 이야기 수({actual_count}) 불일치"
        )

    return result


def _generate_dummy_story_data(
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
) -> dict:
    """더미 스토리 데이터 생성 (API 키 없을 때 폴백)"""
    g = _gender_en(child_gender)
    dummy_stories = [
        f"오늘도 {job_name} {child_name}의 하루가 시작되었어요. 유니폼 단추를 하나하나 채우고 준비를 마치자, 기분이 정말 좋았어요. '좋아, 오늘도 열심히 해 볼까!' {child_name}는 씩씩한 발걸음으로 출발했답니다.",
        f"{child_name}가 도착한 곳에는 {job_name}가 쓰는 도구들이 가득했어요. 하나하나 살펴보니 모두 신기한 것들이었어요. '이건 뭐에 쓰는 거예요?' {child_name}가 호기심 가득한 눈으로 물었답니다.",
        f"선배가 {child_name}에게 중요한 도구를 건네주었어요. '이건 {job_name}의 가장 소중한 도구야. 잘 써 봐!' {child_name}는 두 손으로 소중히 받으며 고개를 끄덕였어요. 이 도구와 함께라면 뭐든 할 수 있을 것 같았어요.",
        f"{child_name}는 친구들 앞에서 {job_name}가 하는 일을 설명해 주었어요. 친구들은 눈을 동그랗게 뜨고 '와, 정말 멋지다!'라고 소리쳤어요. {child_name}는 뿌듯한 마음에 어깨가 으쓱해졌답니다.",
        f"드디어 {child_name}에게 첫 번째 임무가 주어졌어요! 심장이 콩닥콩닥 뛰었지만, 심호흡을 하고 용기를 냈어요. '할 수 있어!' {child_name}는 스스로에게 속삭이며 힘차게 출발했답니다.",
        f"{child_name}는 열심히 일하면서 {job_name}의 일이 얼마나 소중한지 깨달았어요. 누군가를 돕고 나니 마음이 따뜻해졌어요. '이런 기분이구나!' {child_name}는 환하게 웃으며 더 열심히 했답니다.",
        f"그런데 갑자기 어려운 문제가 생겼어요! 모두가 걱정했지만, {child_name}는 당황하지 않고 차분하게 생각했어요. '분명 방법이 있을 거야.' {child_name}는 이마에 손을 대고 곰곰이 생각했답니다.",
        f"{child_name}는 번뜩이는 아이디어로 문제를 해결했어요! '해냈다!' 주변 사람들이 모두 박수를 쳐 주었어요. {child_name}의 얼굴에 환한 미소가 퍼졌어요. 세상에서 가장 기쁜 순간이었답니다.",
        f"사람들이 {child_name}에게 다가와 고마움을 전했어요. '정말 고마워, {child_name}!' 따뜻한 말 한마디에 {child_name}의 마음이 꽉 찼어요. 눈시울이 살짝 뜨거워졌지만, 행복한 눈물이었답니다.",
        f"{child_name}는 하루를 마무리하며 오늘 있었던 일들을 떠올렸어요. 처음에는 떨렸지만, 열심히 해 냈어요. {job_name}가 되어 사람들의 웃음을 만들 수 있다는 게 정말 행복했답니다.",
        f"노을이 물드는 하늘 아래, {child_name}는 가만히 별이 뜨기를 기다렸어요. 첫 번째 별이 반짝이자, {child_name}는 두 손을 모으고 속삭였어요. '내일도 멋진 {job_name}로서, 모든 사람들을 웃게 만들 거야.' {child_name}의 다짐은 별빛처럼 반짝반짝 빛났답니다.",
    ]

    stories = []
    for i, text in enumerate(dummy_stories):
        stories.append({
            "story_number": i + 1,
            "text": text,
        })

    return {
        "title": f"{job_name} {child_name}의 하루",
        "stories": stories,
    }


def generate_story_with_gpt_or_dummy(
    child_name: str,
    job_name: str,
    plot_input: str,
    art_style: Optional[str] = None,
    child_age: int = 6,
    child_gender: str = "male",
) -> dict:
    """API 키가 있으면 GPT-4o, 없으면 더미 스토리를 반환한다.

    Returns:
        {"title": str, "stories": [{"story_number": int, "text": str}, ...]}

    Raises:
        StoryGenerationError: API 키가 있는데 호출 실패 시
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 스토리 폴백")
        return _generate_dummy_story_data(child_name, job_name, child_age, child_gender)

    return generate_story_with_gpt(
        child_name=child_name,
        job_name=job_name,
        plot_input=plot_input,
        art_style=art_style,
        child_age=child_age,
        child_gender=child_gender,
    )


# ──────────────────────────────────────────────
# scene_description 생성 (그림 생성 직전에 호출)
# ──────────────────────────────────────────────

class SceneDescriptionEntry(BaseModel):
    story_number: int
    scene_description: str


class SceneDescriptionOutput(BaseModel):
    scenes: list[SceneDescriptionEntry]


def _build_scene_description_prompt(
    stories: list[dict],
    child_name: str,
    job_name: str,
    art_style: str,
    child_age: int,
    child_gender: str,
) -> str:
    """scene_description 생성용 프롬프트를 구성한다."""
    gender_en = _gender_en(child_gender)
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "illustration style")

    stories_text = "\n".join(
        f"  이야기 {s['story_number']}: {s['text']}" for s in stories
    )

    return f"""당신은 동화책 일러스트 프롬프트 전문가입니다.
아래 한국어 동화 텍스트를 읽고, 각 이야기에 대한 영어 scene_description을 생성하세요.

## 주인공 정보
- 이름: {child_name}
- 나이: {child_age}세
- 성별: {gender_en}
- 직업: {job_name}
- 그림체: {art_keywords}

## scene_description 규칙
- 영어로 작성하세요 (이미지 생성 AI에 전달됨).
- 캐릭터의 외형, 표정, 동작, 배경을 구체적으로 묘사하세요.
- 캐릭터는 항상 {child_age}세 {gender_en} 모습이어야 합니다 (직업 복장을 입은 {gender_en}).
- 캐릭터를 묘사할 때 "a {gender_en} (age {child_age})"로 표현하세요.
- 텍스트 배치 영역(상단 또는 하단)을 고려한 구도를 명시하세요.
- 각 장면이 이전 장면과 다른 배경/상황이 되도록 다양하게 묘사하세요.
- 그림체 스타일: {art_keywords}

## 한국어 이야기 텍스트
{stories_text}

정확히 {len(stories)}개의 scene_description을 생성하세요. story_number는 위와 동일하게 매칭하세요."""


def generate_scene_descriptions(
    stories: list[dict],
    child_name: str,
    job_name: str,
    art_style: str,
    child_age: int,
    child_gender: str,
) -> list[str]:
    """확정된 한국어 텍스트를 기반으로 영어 scene_description을 생성한다.

    Args:
        stories: [{"text": "한국어 텍스트", "story_number": int}, ...]
        child_name: 아이 이름
        job_name: 직업명
        art_style: 그림체
        child_age: 나이
        child_gender: 성별

    Returns:
        scene_description 문자열 리스트 (stories와 동일 순서)
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 scene_description 폴백")
        gender_en = _gender_en(child_gender)
        return [
            f"A {gender_en} (age {child_age}) dressed as a {job_name}, scene {s['story_number']}"
            for s in stories
        ]

    prompt = _build_scene_description_prompt(
        stories=stories,
        child_name=child_name,
        job_name=job_name,
        art_style=art_style,
        child_age=child_age,
        child_gender=child_gender,
    )

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        response = client.beta.chat.completions.parse(
            model=settings.TEXT_MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format=SceneDescriptionOutput,
        )

        parsed = response.choices[0].message.parsed

        # 비용 모니터링
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

    except Exception as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_story_call(success=False, error=str(e))
        logger.error(f"scene_description 생성 실패: {e}")
        raise StoryGenerationError(f"scene_description 생성 중 오류가 발생했습니다: {e}")

    if parsed is None:
        raise StoryGenerationError("scene_description 생성 결과가 비어 있습니다")

    # story_number 순서로 정렬하여 반환
    scene_map = {s.story_number: s.scene_description for s in parsed.scenes}
    return [scene_map.get(s["story_number"], "") for s in stories]


def generate_single_scene_description(
    text: str,
    child_name: str,
    job_name: str,
    art_style: str,
    child_age: int,
    child_gender: str,
) -> str:
    """단일 이야기 텍스트에 대한 scene_description을 생성한다.

    개별 페이지 이미지 재생성 시 사용.
    """
    results = generate_scene_descriptions(
        stories=[{"text": text, "story_number": 1}],
        child_name=child_name,
        job_name=job_name,
        art_style=art_style,
        child_age=child_age,
        child_gender=child_gender,
    )
    return results[0] if results else ""
