"""AI 캐릭터 시트 생성 서비스 (GPT Image)

아이 사진을 선택한 그림체로 변환하여 캐릭터 시트를 생성한다.
images.edit 엔드포인트를 사용하여 참조 이미지(아이 사진) 기반으로 일러스트를 생성한다.
OPENAI_API_KEY가 없으면 호출하지 않는다.
"""
import base64
import logging
from pathlib import Path

from openai import OpenAI, BadRequestError

from app.config import get_settings

logger = logging.getLogger(__name__)


class CharacterGenerationError(Exception):
    """캐릭터 시트 생성 실패 시 발생하는 예외"""
    pass


# ──────────────────────────────────────────────
# 그림체 스타일 키워드 매핑
# ──────────────────────────────────────────────
ART_STYLE_KEYWORDS = {
    "watercolor": "watercolor illustration, soft warm tones, gentle brushstrokes",
    "pastel": "soft pastel illustration, dreamy muted tones, gentle chalky texture",
    "crayon": "crayon drawing, childlike texture, bold colors",
    "3d": "3D render, Pixar style, soft lighting, rounded shapes",
    "cartoon": "cartoon style, cel-shaded, vibrant colors, clean outlines",
}

def _get_job_description(job_name: str, job_name_en: str = "", job_outfit: str = "") -> tuple:
    """직업명에 대한 영어 이름과 복장 묘사를 반환한다.

    Book 테이블의 job_name_en, job_outfit 필드에서 가져온 값을 사용한다.
    값이 없으면 한글 직업명으로 폴백한다.
    """
    en = job_name_en or job_name
    outfit = job_outfit or f"dressed as a {job_name}"
    return (en, outfit)


def _build_character_prompt(
    art_style: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> str:
    """캐릭터 시트 생성용 프롬프트를 구성한다."""
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "illustration style")
    job_en, job_outfit_desc = _get_job_description(job_name, job_name_en, job_outfit)
    gender_en = "boy" if child_gender == "male" else "girl"

    prompt = (
        f"Transform this child into a {art_keywords} storybook character illustration. "
        f"The character is a {gender_en} (age {child_age}), a {job_en}, {job_outfit_desc}. "
        f"Full body, front-facing pose. Solid pastel-colored background. "
        f"Preserve the child's facial features as much as possible while applying the illustration style. "
        f"The character should look like a {gender_en} (age {child_age}), not an adult. "
        f"High quality children's book illustration."
    )

    return prompt


def generate_character_image(
    photo_path: str,
    art_style: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> bytes:
    """GPT Image images.edit을 사용하여 캐릭터 시트를 생성한다.

    Args:
        photo_path: 아이 원본 사진 파일 경로
        art_style: 그림체 스타일 (watercolor, pencil, crayon, 3d, cartoon)
        job_name: 직업명 (한글)
        job_name_en: 영어 직업명 (DB에서 가져옴)
        job_outfit: 복장 묘사 (DB에서 가져옴)

    Returns:
        생성된 캐릭터 시트 PNG 이미지 바이트

    Raises:
        CharacterGenerationError: API 호출 실패 또는 콘텐츠 필터링 거부 시
    """
    settings = get_settings()

    prompt = _build_character_prompt(art_style, job_name, child_age, child_gender, job_name_en, job_outfit)

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        # 아이 사진 파일을 열어서 images.edit에 전달
        photo_file = open(photo_path, "rb")
        try:
            response = client.images.edit(
                model="gpt-image-1-mini",
                image=photo_file,
                prompt=prompt,
                size="1024x1024",
                quality="medium",
                output_format="png",
            )
        finally:
            photo_file.close()

        # base64 인코딩된 이미지 디코딩
        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)

        # 비용 모니터링 로깅
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_character_call(image_count=1, success=True)

        return image_bytes

    except BadRequestError as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_character_call(success=False, error=str(e))
        error_msg = str(e)
        if "content_policy" in error_msg.lower() or "safety" in error_msg.lower():
            logger.warning(f"캐릭터 생성 콘텐츠 정책 위반: {error_msg}")
            raise CharacterGenerationError(
                "콘텐츠 정책에 의해 이미지를 생성할 수 없습니다. 다른 사진을 사용해주세요."
            )
        logger.error(f"GPT Image API 오류: {error_msg}")
        raise CharacterGenerationError(f"캐릭터 시트 생성 중 오류가 발생했습니다: {error_msg}")

    except CharacterGenerationError:
        raise

    except Exception as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_character_call(success=False, error=str(e))
        logger.error(f"GPT Image API 호출 실패: {e}")
        raise CharacterGenerationError(f"캐릭터 시트 생성 중 오류가 발생했습니다: {e}")
