"""AI 줄거리 생성 서비스 (GPT-4o-mini)

직업 정보를 기반으로 동화 줄거리 후보 4개를 생성한다.
Structured Outputs로 응답을 파싱한다.
OPENAI_API_KEY가 없으면 더미 데이터를 반환한다.
"""
import logging
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)


class PlotCandidate(BaseModel):
    plot_number: int
    title: str
    description: str


class PlotOutput(BaseModel):
    plots: list[PlotCandidate]


# ──────────────────────────────────────────────
# Few-shot 예시 (3개 직업 × 4개 줄거리)
# ──────────────────────────────────────────────

FEW_SHOT = """### 소방관
1. 빵집 화재 진압: 마을 빵집에서 갑자기 불이 나고, 주인공이 소방차를 타고 출동합니다. 거센 불길 속에서 호스를 잡고 진화하며, 연기 가득한 안쪽에서 강아지를 꼭 껴안고 웅크린 아이를 발견해 둘 다 안전하게 구출합니다.
2. 아파트 구조: 높은 아파트에서 화재 신고가 들어옵니다. 사다리차를 타고 올라가 연기 가득한 층에서 어린아이를 안고 내려오고, 가족이 눈물을 흘리며 감사합니다.
3. 산불 진화: 가을 산에서 큰 산불이 번지고, 헬기 팀과 함께 물을 뿌리며 산을 지킵니다. 밤새 불과 싸운 뒤 새벽에 마지막 불꽃이 꺼지자, 동료들과 손을 잡고 기뻐합니다.
4. 지진 구조: 갑작스러운 지진으로 건물이 무너지고, 구조대와 함께 잔해 속에 갇힌 사람들을 찾아냅니다. 작은 목소리를 따라가 아이를 구출하고, 가족과 재회하는 장면에 모두가 눈물을 흘립니다.

### 의사
1. 응급 수술: 교통사고로 다친 환자가 응급실에 실려 옵니다. 주인공이 침착하게 수술을 집도하여 환자를 살려내고, 보호자가 깊이 고개를 숙이며 감사 인사를 합니다.
2. 감염병 대응: 마을에 원인 모를 열병이 퍼지자, 주인공이 밤낮없이 환자를 돌보며 원인을 찾아냅니다. 마침내 치료법을 발견하고 마을 사람들이 하나둘 건강을 되찾습니다.
3. 오지 의료봉사: 병원이 없는 먼 시골 마을에 의료 장비를 싣고 찾아갑니다. 오랫동안 아팠던 어르신들을 한 명 한 명 치료하고, 떠날 때 마을 사람들이 길가에 나와 손을 흔듭니다.
4. 심장 수술: 태어날 때부터 심장이 약한 아기의 수술을 맡습니다. 수 시간에 걸친 수술 끝에 아기의 심장이 힘차게 뛰기 시작하자, 수술실에 환호가 터집니다.

### 요리사
1. 요리 대회 우승: 전국 요리 대회 결승에 올라 제한 시간 안에 자신만의 특별한 코스를 완성합니다. 심사위원들이 한 입에 감탄하며 우승 트로피를 건네줍니다.
2. 귀빈 접대: 외국에서 온 귀한 손님이 레스토랑을 방문합니다. 긴장되지만 최고의 한식 코스를 정성껏 만들자, 손님이 "이렇게 맛있는 음식은 처음이에요"라며 극찬합니다.
3. 새 메뉴 개발: 채소를 싫어하는 사람들을 위해 채소가 맛있어지는 비밀 레시피를 연구합니다. 완성된 요리를 먹은 손님들이 "이게 채소라고?"라며 접시를 싹 비웁니다.
4. 축제 총괄: 마을 축제의 음식 총책임을 맡습니다. 주방 팀을 이끌며 수백 인분의 특별 요리를 준비하고, 축제장이 맛있는 냄새로 가득 차며 사람들이 행복해합니다."""


SYSTEM_PROMPT = """당신은 아동용 동화책의 줄거리를 제안하는 작가입니다.

## 세계관
- 주인공은 아이의 모습이지만, 이미 해당 직업의 전문가입니다.
- "꿈", "되고 싶어요", "어른이 되면" 같은 표현은 절대 금지입니다.
- 주인공은 이미 그 직업으로 능숙하게 일하고 있습니다.
- 동료나 부하 직원은 있을 수 있지만, "친구들과 함께" 같은 학교 느낌은 금지입니다.

## 줄거리 규칙
- 정확히 4개의 줄거리 후보를 생성하세요.
- 각 줄거리는 서로 다른 상황/테마여야 합니다 (위기, 도전, 감동 등).
- 각 줄거리는 제목(짧은 키워드)과 설명(2~3문장)으로 구성합니다.
- 설명은 24페이지 동화책 전체의 큰 줄기를 요약합니다.
- 해당 직업의 실제 활동을 구체적으로 반영하세요.
- 타겟 연령: 5~7세. 폭력, 공포, 부정적 결말은 금지합니다."""


def generate_plots_with_gpt(
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
) -> dict:
    """GPT-4o-mini로 줄거리 후보 4개를 생성한다."""
    settings = get_settings()
    gender_ko = "남자아이" if child_gender == "male" else "여자아이"

    user_prompt = f"""## 예시 (3개 직업 × 4개 줄거리)
{FEW_SHOT}

---

## 실제 요청
- 아이 이름: {child_name}
- 나이: {child_age}세 {gender_ko}
- 직업: {job_name}

이 직업으로 가능한 줄거리 4개를 생성해주세요. 각 줄거리는 서로 다른 상황이어야 합니다."""

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
        )

        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=1024,
            response_format=PlotOutput,
        )

        parsed = response.choices[0].message.parsed

        # 비용 로깅
        from app.services.cost_monitor import get_cost_monitor
        monitor = get_cost_monitor()
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_tokens", 0) if usage else 0
        monitor.log_story_call(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            success=True,
        )
        logger.info(f"[ai_plot] 줄거리 생성 완료: {job_name}, tokens={total_tokens}")

    except Exception as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_story_call(success=False, error=str(e))
        logger.error(f"[ai_plot] 줄거리 생성 실패: {e}")
        raise

    if parsed is None:
        raise RuntimeError("줄거리 생성 결과가 비어 있습니다")

    return parsed.model_dump()


def _generate_dummy_plots(job_name: str) -> dict:
    """API 키 없을 때 더미 줄거리 반환."""
    return {
        "plots": [
            {
                "plot_number": 1,
                "title": f"{job_name}의 특별한 하루",
                "description": f"{job_name}로서 평범하지만 특별한 하루를 보냅니다. 작은 사건들을 해결하며 보람을 느끼고, 하루를 마무리하며 내일을 기대합니다.",
            },
            {
                "plot_number": 2,
                "title": f"위기를 극복하는 {job_name}",
                "description": f"예상치 못한 큰 위기가 찾아옵니다. 주인공이 침착하게 대처하며 위기를 해결하고, 동료들과 함께 기뻐합니다.",
            },
            {
                "plot_number": 3,
                "title": f"{job_name}의 첫 도전",
                "description": f"지금까지 해보지 못한 새로운 도전에 나섭니다. 어려움도 있지만 끝까지 해내며 한 단계 성장합니다.",
            },
            {
                "plot_number": 4,
                "title": f"감동을 전하는 {job_name}",
                "description": f"도움이 필요한 사람을 만나 정성껏 돕습니다. 감사 인사를 받으며 이 직업을 선택하길 잘했다고 느낍니다.",
            },
        ],
    }


def generate_plots(
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
) -> dict:
    """줄거리 생성 — API 키 있으면 GPT, 없으면 더미."""
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 줄거리 폴백")
        return _generate_dummy_plots(job_name)

    return generate_plots_with_gpt(
        child_name=child_name,
        job_name=job_name,
        child_age=child_age,
        child_gender=child_gender,
    )
