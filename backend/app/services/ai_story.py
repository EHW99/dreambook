"""AI 스토리 생성 서비스 (GPT-4o)

OpenAI GPT-4o를 사용하여 동화 스토리를 생성한다.
24페이지 고정 구성: 제목(1p) + [그림+이야기]×11(2~23p) + 판권(24p)
LLM은 이야기 11개 + scene_description 11개를 생성한다.
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
    scene_description: str


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
# 각 직업마다 이야기 1(도입), 6(전환), 9(절정), 11(결말)
# 톤, 분량(3~4문장), 도입/절정/결말 품질의 기준을 보여준다
# ──────────────────────────────────────────────
FEW_SHOT_FIREFIGHTER = """{
  "title": "용감한 소방관 하준이",
  "stories": [
    {
      "story_number": 1,
      "text": "오늘도 소방관 하준이의 하루가 시작되었어요. 빨간 소방복의 단추를 하나하나 채우고, 반짝이는 헬멧을 쓰자 기분이 정말 좋았어요. 소방서 앞에는 커다란 빨간 소방차가 하준이를 기다리고 있었어요. '좋아, 오늘도 마을을 지키러 출발이다!' 하준이는 힘차게 소방차에 올라탔답니다.",
      "scene_description": "A confident child firefighter (age 6) in a bright red uniform buttoning up their coat, standing in front of a gleaming red fire truck at the fire station entrance. The child has a determined and cheerful expression, morning sunlight casting a warm glow. Background: the fire station with its large open bay doors, a clear blue sky, other firefighter equipment neatly organized. Composition: character on the left, the impressive fire truck behind them, warm morning light, space at top for text."
    },
    {
      "story_number": 6,
      "text": "소방서로 돌아온 하준이는 소방차를 꼼꼼히 점검했어요. 호스에서 물이 잘 나오는지, 사다리가 높이높이 올라가는지 하나하나 살폈어요. 선배 소방관이 '하준이, 장비를 잘 관리하는 것도 사람들을 지키는 일이야'라고 말해 주었어요. 하준이는 고개를 끄덕이며 더 열심히 점검했답니다.",
      "scene_description": "A child firefighter carefully inspecting a fire truck, crouched down checking the hose connection with a focused and serious expression. An adult firefighter stands nearby with a warm encouraging smile. Background: inside a spacious fire station garage with sunlight streaming through the open bay door, other equipment on walls, a Dalmatian dog sitting nearby. Composition: child on the right, fire truck dominating the left, adult figure in mid-ground, space at bottom for text."
    },
    {
      "story_number": 9,
      "text": "삐뽀삐뽀! 빵집에서 큰불이 났어요! 하준이는 소방차에서 뛰어내려 무거운 호스를 꽉 잡았어요. 뜨거운 연기가 자욱했지만, 안에 할머니가 갇혀 계신다는 말에 하준이는 물러서지 않았어요. '제가 꼭 구해 드릴게요!' 하준이는 물을 힘껏 뿌리며 연기 속으로 용감하게 뛰어 들어갔답니다.",
      "scene_description": "A brave child firefighter (age 6) charging into a smoke-filled bakery doorway, gripping a fire hose with both hands and spraying a powerful stream of water. Flames flicker from the windows above, and thick gray smoke billows into the sky. Fellow firefighters in the background operate the fire truck and cheer the child on. The child's expression is fierce and determined, helmet reflecting the orange glow of the fire. Background: a small-town street with concerned neighbors watching from a safe distance, fire truck with flashing red lights. Composition: dynamic action shot, child running from the right toward the burning building on the left, dramatic lighting from the flames, space at top for text."
    },
    {
      "story_number": 11,
      "text": "노을이 물드는 저녁, 하준이는 소방서 옥상에 올라 반짝이는 마을을 내려다보았어요. 오늘 하루 동안 도와준 사람들의 환한 웃음이 떠올라 마음이 따뜻해졌어요. 하준이는 헬멧을 꼭 안으며 작은 목소리로 속삭였어요. '이 마을은 내가 지킨다. 내일도, 모레도, 언제까지나.'",
      "scene_description": "A child firefighter standing on a fire station rooftop, hugging their yellow helmet close to their chest with a deeply content and peaceful smile. Background: a breathtaking sunset painting the sky in layers of orange, pink, and purple; the small town below has warm golden lights twinkling in windows. A few birds fly across the colorful sky. Composition: character silhouetted on the left gazing at the vast sunset on the right, cinematic wide-angle feel, space at bottom for text."
    }
  ]
}"""

FEW_SHOT_DOCTOR = """{
  "title": "다정한 의사 수아",
  "stories": [
    {
      "story_number": 1,
      "text": "수아 의사 선생님의 하루가 밝게 시작되었어요. 하얀 가운을 입고 청진기를 목에 걸자, 병원 복도에서 간호사가 '수아 선생님, 오늘 진료 환자분들이 기다리고 있어요!'라고 알려주었어요. 수아는 환하게 웃으며 진료실 문을 열었어요. '자, 오늘도 환자분들을 건강하게 만들어 드리자!' 수아의 목소리에 병원이 활기를 띠었답니다.",
      "scene_description": "A small child doctor (age 6) in a white coat with a stethoscope, walking confidently down a bright hospital corridor. A nurse beside them is gesturing toward a consultation room door. The child has a warm, professional smile. Background: a modern hospital hallway with clean walls, medical posters, sunflowers in vases, and sunlight streaming through large windows. Composition: child walking from left to right down the corridor, nurse beside them, welcoming and bright atmosphere, space at top for text."
    },
    {
      "story_number": 6,
      "text": "수아는 청진기를 귀에 꽂고 환자의 가슴에 살며시 대 보았어요. '심장이 튼튼하게 뛰고 있어요, 걱정 마세요!' 수아의 다정한 말에 불안해하던 환자의 얼굴이 조금씩 밝아졌어요. 수아는 처방전을 꼼꼼히 쓰며 말했어요. '이 약을 드시면 금방 나으실 거예요.' 환자의 보호자가 '감사합니다, 수아 선생님' 하고 고개를 숙이자 수아는 환하게 웃었답니다.",
      "scene_description": "A child doctor (age 6) in a white coat gently placing a stethoscope on a patient's chest in a bright examination room. The patient sitting on the exam bed looks relieved and is beginning to smile. The child doctor writes a prescription on a clipboard with a caring and professional expression. A family member stands beside the bed, hands clasped in gratitude. Background: a clean, modern clinic with pastel-colored walls, anatomical posters, warm sunlight through the window. Composition: child doctor on the left with stethoscope, patient in the center on the bed, family member on the right, warm and reassuring atmosphere, space at bottom for text."
    },
    {
      "story_number": 9,
      "text": "그때 복도에서 다급한 목소리가 들려왔어요. '수아 선생님, 응급 환자입니다!' 교통사고로 크게 다친 환자가 응급실에 실려 왔어요. 수아는 떨리는 마음을 꾹 누르고 재빨리 수술 준비를 지시했어요. 집중해서 수술을 진행하고, 마침내 환자의 상태가 안정되자 수술실에 안도의 한숨이 퍼졌답니다.",
      "scene_description": "A child doctor (age 6) in a white coat and surgical mask, standing in a brightly lit operating room with intense focus, hands raised ready for surgery. Medical monitors beep in the background, a surgical team of nurses assists. The child doctor's eyes show fierce determination above the mask. Background: a modern operating room with overhead surgical lights, medical instruments neatly arranged, a sense of high-stakes urgency. Composition: dramatic close-up angle, child doctor in the center under bright surgical light, team around them, tension and professionalism, space at bottom for text."
    },
    {
      "story_number": 11,
      "text": "하루가 끝나고, 수아는 병원 창가에 앉아 노을을 바라보았어요. 오늘 수술이 성공해서 환자가 웃으며 퇴원하던 모습이 자꾸자꾸 떠올랐어요. 수아는 청진기를 가만히 만지며 생각했어요. '아픈 사람들의 웃음을 되찾아 주는 것, 이게 바로 내가 하는 일이야.' 병원 밖으로 첫 번째 별이 반짝 빛났답니다.",
      "scene_description": "A child doctor sitting peacefully on a wide hospital windowsill, legs dangling, gently holding their stethoscope and gazing at a beautiful sunset outside. Their expression is soft and thoughtful, with a gentle smile. Background: through the large window, a stunning sunset with the first evening star visible; inside, a warm lamp casts a golden glow on the child. A thank-you card from a patient is propped up on the windowsill beside them. Composition: character centered at the window, warm interior light contrasting with the colorful sky outside, intimate and peaceful mood, space at top for text."
    }
  ]
}"""

FEW_SHOT_CHEF = """{
  "title": "꼬마 요리사 지우의 맛있는 하루",
  "stories": [
    {
      "story_number": 1,
      "text": "요리사 지우는 오늘도 신나게 주방 문을 열었어요. 하얀 요리사 모자를 쓰고 앞치마를 두르자, 벌써부터 맛있는 냄새가 코끝을 간질였어요. 주방에는 알록달록한 채소와 싱싱한 과일이 가득했어요. '좋아, 오늘은 특별한 요리를 만들어 볼 거야!' 지우는 소매를 걷어붙이며 활짝 웃었답니다.",
      "scene_description": "A cheerful child chef (age 6) wearing a tall white chef hat and checkered apron, pushing open the doors of a bright professional kitchen with an eager smile. Colorful fresh vegetables, fruits, and ingredients are arranged beautifully on the counters. Background: a spacious kitchen with copper pots hanging from the ceiling, steam rising softly, warm lighting. Composition: child entering from the left pushing doors open, the magnificent kitchen spread before them, warm and inviting atmosphere, space at top for text."
    },
    {
      "story_number": 6,
      "text": "지우는 커다란 볼에 밀가루와 달걀을 넣고 열심히 반죽했어요. 하얀 밀가루가 코끝에 묻었지만 지우는 신경 쓰지 않았어요. 반죽을 동글동글 모양을 내자, 예쁜 쿠키가 완성되었어요. '이건 별 모양, 이건 하트 모양!' 지우는 하나하나 정성껏 만들며 노래를 불렀답니다.",
      "scene_description": "A child chef energetically kneading dough in a large mixing bowl, with flour dusted on their nose and cheeks. Star and heart shaped cookies are arranged on a baking tray beside them. The child is singing happily while working. Background: a warm kitchen counter with bowls of colorful sprinkles, cookie cutters in various shapes, an oven glowing with warmth behind them. Flour particles floating in a beam of sunlight. Composition: close-up of the child and the baking workspace, warm and cozy kitchen atmosphere, space at bottom for text."
    },
    {
      "story_number": 9,
      "text": "드디어 요리 경연대회 결승전! 심사위원들 앞에서 지우의 손이 바쁘게 움직였어요. 프라이팬을 높이 들어 올려 휙! 하고 볶음밥을 공중에 날리자, 관객석에서 '우와!' 하는 탄성이 터져 나왔어요. 마지막으로 예쁜 접시에 정성껏 담아내자, 심사위원들이 한 입 먹고 눈을 동그랗게 떴어요. '우승은 꼬마 요리사 지우!' 트로피를 높이 들어 올린 지우의 눈에 기쁨의 눈물이 반짝였답니다.",
      "scene_description": "A child chef (age 6) on a grand cooking competition stage, triumphantly holding a golden trophy above their head with both hands, tears of joy sparkling in their eyes. Confetti rains down from above. On the cooking station beside them, a beautifully plated dish gleams under the stage lights. Three impressed judges at a long table are standing and applauding enthusiastically. A large cheering audience fills the background with raised hands. Background: a dazzling competition stage with bright spotlights, a giant banner reading 'COOKING CHAMPIONSHIP', colorful confetti everywhere. Composition: child in the center holding the trophy high, judges on the left applauding, audience behind, dramatic stage lighting with golden spotlight on the child, space at top for text."
    },
    {
      "story_number": 11,
      "text": "해가 질 무렵, 지우는 레스토랑 창가에 앉아 오늘 하루를 떠올렸어요. 손님들이 '세상에서 제일 맛있어요!'라며 빈 접시를 보여주던 모습이 눈에 선했어요. 지우는 수줍게 웃으며 말했어요. '맛있는 음식으로 사람들을 행복하게 만드는 것, 이게 바로 요리사인 나의 하루야.' 주방에 퍼진 달콤한 향기처럼, 지우의 따뜻한 마음도 온 세상에 퍼져 나갔답니다.",
      "scene_description": "A child chef sitting by the window of their restaurant at sunset, looking out with a content and proud expression. Empty plates on nearby tables show satisfied customers have left. The warm glow of sunset fills the elegant restaurant interior. A few thank-you notes from customers are pinned on the kitchen board behind. Background: a cozy restaurant interior bathed in golden sunset light, clean kitchen visible through the pass, warm and peaceful atmosphere. Composition: child on the left gazing out the window, the restaurant stretching behind, golden hour light, space at top for text."
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

## 줄거리 준수
- 사용자가 제공한 줄거리 방향이 있다면, 반드시 그 줄거리를 중심으로 11개 이야기를 전개하세요.
- 줄거리에 나온 핵심 사건과 상황이 이야기 속에 자연스럽게 녹아들어야 합니다.
- 줄거리를 임의로 바꾸거나 무시하지 마세요.

## 금지 사항
- 폭력, 공포, 부정적 결말 금지
- 성인 수준의 어휘나 개념 금지
- 비현실적인 직업 묘사 금지 (소방관이 불을 마법으로 끄는 등)
- 성별/인종 고정관념 금지

## scene_description 규칙
- 영어로 작성하세요 (이미지 생성 AI에 전달됨).
- 캐릭터의 외형, 표정, 동작, 배경을 구체적으로 묘사하세요.
- 캐릭터는 항상 {child_age}세 {gender_en} 모습이어야 합니다 (직업 복장을 입은 {gender_en}).
- 캐릭터를 묘사할 때 "a {gender_en} (age {child_age})"로 표현하세요.
- 텍스트 배치 영역(상단 또는 하단)을 고려한 구도를 명시하세요.
- 각 장면이 이전 장면과 다른 배경/상황이 되도록 다양하게 묘사하세요."""

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
다음은 소방관, 의사, 요리사 동화의 이야기 1, 6, 9, 11번 예시입니다.
각 이야기의 톤, 분량(3~4문장), 도입/절정/결말의 감성을 참고하세요:

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
각 이야기의 text는 한국어 3~4문장으로 장면을 생생하게 묘사하고, scene_description은 영어로 구체적인 장면 묘사입니다.
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
        {"title": str, "stories": [{"story_number": int, "text": str, "scene_description": str}, ...]}

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
            model="gpt-4o-mini",
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
        (f"오늘도 {job_name} {child_name}의 하루가 시작되었어요. 유니폼 단추를 하나하나 채우고 준비를 마치자, 기분이 정말 좋았어요. '좋아, 오늘도 열심히 해 볼까!' {child_name}는 씩씩한 발걸음으로 출발했답니다.",
         f"A confident {g} (age {child_age}) dressed as a {job_name}, getting ready for work with a cheerful determined expression, bright workplace entrance with morning sunlight"),
        (f"{child_name}가 도착한 곳에는 {job_name}가 쓰는 도구들이 가득했어요. 하나하나 살펴보니 모두 신기한 것들이었어요. '이건 뭐에 쓰는 거예요?' {child_name}가 호기심 가득한 눈으로 물었답니다.",
         f"A {g} {job_name} exploring their new workspace with sparkling curious eyes, surrounded by professional tools and equipment, bright and welcoming setting"),
        (f"선배가 {child_name}에게 중요한 도구를 건네주었어요. '이건 {job_name}의 가장 소중한 도구야. 잘 써 봐!' {child_name}는 두 손으로 소중히 받으며 고개를 끄덕였어요. 이 도구와 함께라면 뭐든 할 수 있을 것 같았어요.",
         f"A {g} {job_name} carefully receiving an important tool from an adult mentor, holding it with both hands reverently, indoor professional setting with warm light"),
        (f"{child_name}는 친구들 앞에서 {job_name}가 하는 일을 설명해 주었어요. 친구들은 눈을 동그랗게 뜨고 '와, 정말 멋지다!'라고 소리쳤어요. {child_name}는 뿌듯한 마음에 어깨가 으쓱해졌답니다.",
         f"A {g} {job_name} proudly explaining their job to a group of impressed children, the other kids looking up with wide eyes and admiration, outdoor setting with playground"),
        (f"드디어 {child_name}에게 첫 번째 임무가 주어졌어요! 심장이 콩닥콩닥 뛰었지만, 심호흡을 하고 용기를 냈어요. '할 수 있어!' {child_name}는 스스로에게 속삭이며 힘차게 출발했답니다.",
         f"A {g} {job_name} receiving their first mission, looking determined with a mix of nervous excitement, taking a deep breath before starting, busy workplace background"),
        (f"{child_name}는 열심히 일하면서 {job_name}의 일이 얼마나 소중한지 깨달았어요. 누군가를 돕고 나니 마음이 따뜻해졌어요. '이런 기분이구나!' {child_name}는 환하게 웃으며 더 열심히 했답니다.",
         f"A {g} {job_name} actively working and helping others with a warm fulfilled expression, community members smiling gratefully, warm and cozy atmosphere"),
        (f"그런데 갑자기 어려운 문제가 생겼어요! 모두가 걱정했지만, {child_name}는 당황하지 않고 차분하게 생각했어요. '분명 방법이 있을 거야.' {child_name}는 이마에 손을 대고 곰곰이 생각했답니다.",
         f"A {g} {job_name} facing a big challenge, standing calmly with hand on chin in a thinking pose while others around look worried, dramatic but child-friendly scene"),
        (f"{child_name}는 번뜩이는 아이디어로 문제를 해결했어요! '해냈다!' 주변 사람들이 모두 박수를 쳐 주었어요. {child_name}의 얼굴에 환한 미소가 퍼졌어요. 세상에서 가장 기쁜 순간이었답니다.",
         f"A {g} {job_name} celebrating a triumphant moment, jumping with joy while a crowd of people clap and cheer around them, confetti or sparkles in the air, bright and festive mood"),
        (f"사람들이 {child_name}에게 다가와 고마움을 전했어요. '정말 고마워, {child_name}!' 따뜻한 말 한마디에 {child_name}의 마음이 꽉 찼어요. 눈시울이 살짝 뜨거워졌지만, 행복한 눈물이었답니다.",
         f"A {g} {job_name} being thanked by grateful townspeople, receiving hugs and handshakes, the child looking deeply moved with glistening eyes, warm sunset light, town square with flowers"),
        (f"{child_name}는 하루를 마무리하며 오늘 있었던 일들을 떠올렸어요. 처음에는 떨렸지만, 열심히 해 냈어요. {job_name}가 되어 사람들의 웃음을 만들 수 있다는 게 정말 행복했답니다.",
         f"A {g} {job_name} walking along a beautiful sunset path, looking content and reflective, golden hour light casting long warm shadows, peaceful neighborhood scenery"),
        (f"노을이 물드는 하늘 아래, {child_name}는 가만히 별이 뜨기를 기다렸어요. 첫 번째 별이 반짝이자, {child_name}는 두 손을 모으고 속삭였어요. '내일도 멋진 {job_name}로서, 모든 사람들을 웃게 만들 거야.' {child_name}의 다짐은 별빛처럼 반짝반짝 빛났답니다.",
         f"A {g} {job_name} standing on a gentle hilltop under a magnificent twilight sky, hands clasped together making a wish as the first star appears. The child's expression is peaceful, hopeful, and full of quiet determination. Background: layers of purple, orange and indigo sky with a single bright star, town lights twinkling below. Composition: child silhouetted against the vast sky, cinematic and emotional, space at top for text."),
    ]

    stories = []
    for i, (text, scene) in enumerate(dummy_stories):
        stories.append({
            "story_number": i + 1,
            "text": text,
            "scene_description": scene,
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
        {"title": str, "stories": [{"story_number": int, "text": str, "scene_description": str}, ...]}

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
