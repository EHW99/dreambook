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
1. 큰 건물 화재 진압: 높은 건물에서 시뻘건 불길이 치솟고, 주인공이 소방차를 타고 출동합니다. 뜨거운 열기 속에서 호스를 꽉 잡고 불을 꺼 나가며, 연기 가득한 안쪽에 갇힌 사람들을 한 명씩 업고 나옵니다.
2. 홍수 속 구조 작전: 폭우로 마을이 물에 잠기고, 주인공이 구조 보트를 타고 출동합니다. 거센 물살을 헤치며 지붕 위에서 떨고 있는 가족을 발견하고, 밧줄을 던져 한 명 한 명 보트로 끌어올립니다.
3. 산불과의 사투: 가을 산에서 큰 불이 번지고, 헬기 팀과 함께 산 위로 올라갑니다. 뜨거운 바람이 불어오는 속에서 방화선을 만들고 물을 퍼부으며 밤새 불과 싸운 끝에, 새벽녘 마지막 불꽃이 꺼집니다.
4. 사다리차 고층 구출: 높은 아파트에서 화재 신고가 들어오고, 주인공이 사다리차를 끝까지 올려 연기 가득한 창문에 다가갑니다. 겁에 질린 아이를 꼭 안고 사다리를 타고 내려오자, 아래에서 기다리던 가족이 달려옵니다.

### 의사
1. 긴급 수술: 크게 다친 환자가 응급실에 실려 오고, 주인공이 떨리는 마음을 꾹 누르고 수술실에 들어갑니다. 몇 시간에 걸친 수술 끝에 환자의 상태가 안정되자, 수술실에 안도의 한숨이 퍼집니다.
2. 원인 모를 병의 비밀: 마을 아이들이 하나둘 같은 증상으로 쓰러지고, 주인공이 탐정처럼 단서를 추적합니다. 검사 결과를 분석하고 마침내 원인을 밝혀내어 치료약을 처방하자, 아이들이 하나씩 웃음을 되찾습니다.
3. 오지 마을 의료 봉사: 병원이 없는 먼 산골 마을에 의료 장비를 싣고 찾아갑니다. 오랫동안 아팠던 할머니를 진찰하고 정성껏 치료하자, 떠나는 날 마을 사람들이 길가에 나와 손을 흔들며 배웅합니다.
4. 운동회의 영웅: 학교 운동회에서 달리기를 하던 아이가 넘어져 다리를 다칩니다. 주인공이 달려가 침착하게 응급 처치를 하고 병원으로 옮겨 깁스를 해 주자, 아이가 목발을 짚고 웃으며 "선생님 덕분이에요!" 하고 말합니다.

### 요리사
1. 요리 대회 결승전: 전국 요리 대회 결승 무대에 오르고, 제한 시간 안에 자신만의 특별한 코스를 완성합니다. 심사위원이 한 입 먹고 눈이 동그래지며 만점을 주자, 관객석에서 환호가 터집니다.
2. 특별한 손님의 만찬: 유명한 미식가가 레스토랑에 예고 없이 찾아옵니다. 긴장되지만 최고의 재료로 정성껏 코스를 만들자, 그 손님이 "여기 요리가 최고입니다"라며 별점 후기를 남깁니다.
3. 마을 축제 요리 대장: 마을 축제의 음식 총책임을 맡아 수백 인분의 특별 요리를 준비합니다. 주방 팀을 이끌며 거대한 솥에서 요리를 만들고, 축제장이 맛있는 냄새로 가득 차며 사람들이 행복해합니다.
4. 특별한 생일 케이크: 아픈 친구를 위해 세상에서 하나뿐인 생일 케이크를 만듭니다. 밤새 반죽하고 장식하며 정성을 다해 완성한 케이크를 보고, 친구가 눈물을 글썽이며 활짝 웃습니다."""


SYSTEM_PROMPT = """당신은 아동용 동화책의 줄거리를 제안하는 작가입니다.

## 세계관
- 주인공은 아이의 모습이지만, 이미 해당 직업의 전문가입니다.
- "꿈", "되고 싶어요", "어른이 되면" 같은 표현은 절대 금지입니다.
- 주인공은 이미 그 직업으로 능숙하게 일하고 있습니다.
- 동료나 부하 직원은 있을 수 있지만, "친구들과 함께" 같은 학교 느낌은 금지입니다.

## 줄거리 규칙
- 정확히 4개의 줄거리 후보를 생성하세요.
- 각 줄거리는 서로 다른 상황/테마여야 합니다 (일상 업무, 도전, 성장, 보람 등).
- 각 줄거리는 제목(짧은 키워드)과 설명(2~3문장)으로 구성합니다.
- 설명은 24페이지 동화책 전체의 큰 줄기를 요약합니다.
- 해당 직업의 실제 활동을 구체적으로 반영하세요 — 그 직업인이 매일 하는 구체적인 업무와 도구를 묘사합니다.
- 모든 사건은 직업 현장에서 자연스럽게 일어나는 일이어야 합니다. 맥락 없이 갑자기 벌어지는 사건은 넣지 마세요.
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
            model=settings.TEXT_MODEL,
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
