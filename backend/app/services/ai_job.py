"""AI 직업명 영어 변환 서비스 (GPT-4o-mini)

한글 직업명을 영어 직업명 + 복장 묘사로 변환한다.
캐릭터 시트, 일러스트 생성 프롬프트에 사용된다.
"""
import logging

from openai import OpenAI
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)


class JobTranslation(BaseModel):
    job_name_en: str
    job_outfit: str


def translate_job_with_gpt(job_name: str) -> dict:
    """GPT-4o-mini로 직업명을 영어 변환한다.

    Args:
        job_name: 한글 직업명 (예: "소방관", "웹디자이너")

    Returns:
        {"job_name_en": "firefighter", "job_outfit": "wearing a red firefighter helmet and yellow fireproof coat"}
    """
    settings = get_settings()

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,
        )

        response = client.beta.chat.completions.parse(
            model=settings.TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You translate Korean job names into English for children's book illustration prompts.\n"
                        "Return:\n"
                        "- job_name_en: English job title (e.g. 'firefighter')\n"
                        "- job_outfit: Visual description of the job's typical outfit/appearance for illustration "
                        "(e.g. 'wearing a red firefighter helmet and yellow fireproof coat')\n"
                        "Keep job_outfit under 20 words. Focus on visually distinctive clothing/tools.\n\n"
                        "IMPORTANT: The character is a child (age 5-7). "
                        "Never describe revealing, skin-exposing, or tight-fitting clothing. "
                        "Always use full-coverage child-safe alternatives. Examples:\n"
                        "- swimmer → 'wearing a full-body athletic wetsuit, swimming goggles, and a swim cap'\n"
                        "- ballet dancer → 'wearing a long-sleeve leotard with leggings and ballet shoes'\n"
                        "- cheerleader → 'wearing a long-sleeve cheerleading uniform with pants'\n"
                        "- gymnast → 'wearing a full-body gymnastics suit with long sleeves'"
                    ),
                },
                {"role": "user", "content": job_name},
            ],
            temperature=0.3,
            max_tokens=200,
            response_format=JobTranslation,
        )

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("직업 번역 결과가 비어 있습니다")

        result = parsed.model_dump()
        logger.info(f"[ai_job] 직업 번역: {job_name} → {result['job_name_en']}")
        return result

    except Exception as e:
        logger.error(f"[ai_job] 직업 번역 실패: {e}")
        # 폴백: 한글 그대로 사용
        return {
            "job_name_en": job_name,
            "job_outfit": f"dressed as a {job_name}",
        }


def translate_job(job_name: str) -> dict:
    """직업명 영어 변환 — API 키 있으면 GPT, 없으면 폴백."""
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 직업 번역 폴백")
        return {
            "job_name_en": job_name,
            "job_outfit": f"dressed as a {job_name}",
        }

    return translate_job_with_gpt(job_name)
