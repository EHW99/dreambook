"""AI 페이지 일러스트 생성 서비스 (GPT Image)

캐릭터 시트를 참조 이미지로 사용하여 페이지별 일러스트를 생성한다.
images.edit 엔드포인트를 사용한다.
OPENAI_API_KEY가 없으면 None을 반환하여 더미 이미지 폴백을 유도한다.
"""
import base64
import logging

from openai import OpenAI, BadRequestError

from app.services.image_utils import resize_image_for_api, call_with_retry

from app.config import get_settings

logger = logging.getLogger(__name__)


class IllustrationGenerationError(Exception):
    """일러스트 생성 실패 시 발생하는 예외"""
    pass


# ──────────────────────────────────────────────
# 그림체 스타일 키워드 매핑 (ai_character.py와 동일)
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


def _build_illustration_prompt(
    art_style: str,
    scene_description: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> str:
    """페이지 일러스트 생성용 프롬프트를 구성한다.

    ai-guide.md의 규칙을 따른다:
    - 매 페이지에 그림체 키워드 동일하게 포함
    - 캐릭터 외형 묘사 매번 포함
    - 텍스트 배치 영역 확보
    """
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "illustration style")
    job_en, job_outfit_desc = _get_job_description(job_name, job_name_en, job_outfit)
    gender_en = "boy" if child_gender == "male" else "girl"

    prompt = (
        f"{art_keywords} children's book illustration. "
        f"Scene: {scene_description}. "
        f"Character: A {gender_en} named {child_name} (age {child_age}), a {job_en}, {job_outfit_desc}. "
        f"The character should look like the reference image ({gender_en}, age {child_age}). "
        f"Composition: Leave space at the bottom or top for text overlay. "
        f"Background: Detailed background matching the scene. "
        f"High quality children's storybook page illustration. "
        f"No text or letters in the image."
    )

    return prompt


def generate_illustration_image(
    character_sheet_path: str,
    scene_description: str,
    art_style: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> bytes:
    """GPT Image images.edit을 사용하여 페이지 일러스트를 생성한다.

    Args:
        character_sheet_path: 확정된 캐릭터 시트 이미지 파일 경로
        scene_description: 장면 묘사 (영어)
        art_style: 그림체 스타일
        child_name: 아이 이름
        job_name: 직업명 (한글)

    Returns:
        생성된 일러스트 PNG 이미지 바이트

    Raises:
        IllustrationGenerationError: API 호출 실패 시
    """
    settings = get_settings()

    prompt = _build_illustration_prompt(art_style, scene_description, child_name, job_name, child_age, child_gender, job_name_en, job_outfit)

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        photo_buf = resize_image_for_api(character_sheet_path)

        def _api_call():
            photo_buf.seek(0)
            return client.images.edit(
                model=settings.IMAGE_MODEL,
                image=photo_buf,
                prompt=prompt,
                size="1024x1024",
                quality=settings.IMAGE_QUALITY,
                output_format="png",
            )

        response = call_with_retry(_api_call)

        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)

        # 비용 모니터링 로깅
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(image_count=1, success=True)

        return image_bytes

    except BadRequestError as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(success=False, error=str(e))
        error_msg = str(e)
        if "content_policy" in error_msg.lower() or "safety" in error_msg.lower():
            logger.warning(f"일러스트 생성 콘텐츠 정책 위반: {error_msg}")
            raise IllustrationGenerationError(
                "콘텐츠 정책에 의해 이미지를 생성할 수 없습니다."
            )
        logger.error(f"GPT Image API 오류: {error_msg}")
        raise IllustrationGenerationError(f"일러스트 생성 중 오류가 발생했습니다: {error_msg}")

    except IllustrationGenerationError:
        raise

    except Exception as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(success=False, error=str(e))
        logger.error(f"GPT Image API 호출 실패: {e}")
        raise IllustrationGenerationError(f"일러스트 생성 중 오류가 발생했습니다: {e}")


def generate_illustration_or_dummy(
    character_sheet_path: str,
    scene_description: str,
    art_style: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> bytes | None:
    """API 키가 있으면 GPT Image, 없거나 실패하면 None 반환.

    None 반환 시 호출자가 placeholder 이미지를 생성해야 한다.

    Returns:
        성공 시 PNG 이미지 바이트, 실패/미설정 시 None
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 더미 일러스트 폴백")
        return None

    try:
        return generate_illustration_image(
            character_sheet_path=character_sheet_path,
            scene_description=scene_description,
            art_style=art_style,
            child_name=child_name,
            job_name=job_name,
            child_age=child_age,
            child_gender=child_gender,
            job_name_en=job_name_en,
            job_outfit=job_outfit,
        )
    except IllustrationGenerationError as e:
        logger.warning(f"AI 일러스트 생성 실패, 더미 폴백: {e}")
        return None


# ──────────────────────────────────────────────
# 표지 전용
# ──────────────────────────────────────────────

def _build_cover_prompt(
    art_style: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> str:
    """표지 이미지 생성용 프롬프트를 구성한다.

    내지와 달리:
    - scene_description 없음 (장면이 아니라 캐릭터 포트레이트)
    - 정면 포즈, 자신감 있는 표정
    - 단순하고 밝은 배경
    - 이미지 안에 텍스트 금지 (제목/저자는 템플릿이 배치)
    """
    art_keywords = ART_STYLE_KEYWORDS.get(art_style, "illustration style")
    job_en, job_outfit_desc = _get_job_description(job_name, job_name_en, job_outfit)
    gender_en = "boy" if child_gender == "male" else "girl"

    prompt = (
        f"{art_keywords} children's book cover illustration. "
        f"Character: A {gender_en} named {child_name} (age {child_age}), a {job_en}, {job_outfit_desc}. "
        f"The character should look like the reference image ({gender_en}, age {child_age}). "
        f"The character stands front-facing in the center with a confident, happy smile. "
        f"Simple, bright, colorful background with soft gradients. "
        f"High quality children's storybook cover portrait. "
        f"No text, no letters, no words in the image."
    )

    return prompt


def generate_cover_image_ai(
    character_sheet_path: str,
    art_style: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> bytes:
    """표지 전용 이미지를 생성한다.

    내지 일러스트와 동일한 API(images.edit)를 사용하지만,
    표지 전용 프롬프트(_build_cover_prompt)를 사용한다.
    """
    settings = get_settings()

    prompt = _build_cover_prompt(art_style, child_name, job_name, child_age, child_gender, job_name_en, job_outfit)

    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=120.0,
        )

        photo_buf = resize_image_for_api(character_sheet_path)

        def _api_call():
            photo_buf.seek(0)
            return client.images.edit(
                model=settings.IMAGE_MODEL,
                image=photo_buf,
                prompt=prompt,
                size="1024x1024",
                quality=settings.IMAGE_QUALITY,
                output_format="png",
            )

        response = call_with_retry(_api_call)

        b64_data = response.data[0].b64_json
        image_bytes = base64.b64decode(b64_data)

        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(image_count=1, success=True)

        return image_bytes

    except BadRequestError as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(success=False, error=str(e))
        error_msg = str(e)
        if "content_policy" in error_msg.lower() or "safety" in error_msg.lower():
            logger.warning(f"표지 생성 콘텐츠 정책 위반: {error_msg}")
            raise IllustrationGenerationError("콘텐츠 정책에 의해 표지를 생성할 수 없습니다.")
        logger.error(f"GPT Image API 오류 (표지): {error_msg}")
        raise IllustrationGenerationError(f"표지 생성 중 오류가 발생했습니다: {error_msg}")

    except IllustrationGenerationError:
        raise

    except Exception as e:
        from app.services.cost_monitor import get_cost_monitor
        get_cost_monitor().log_illustration_call(success=False, error=str(e))
        logger.error(f"GPT Image API 호출 실패 (표지): {e}")
        raise IllustrationGenerationError(f"표지 생성 중 오류가 발생했습니다: {e}")


def generate_cover_or_dummy(
    character_sheet_path: str,
    art_style: str,
    child_name: str,
    job_name: str,
    child_age: int = 6,
    child_gender: str = "male",
    job_name_en: str = "",
    job_outfit: str = "",
) -> bytes | None:
    """표지 생성 — API 키 있으면 GPT, 없거나 실패하면 None."""
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 미설정 — 표지 더미 폴백")
        return None

    try:
        return generate_cover_image_ai(
            character_sheet_path=character_sheet_path,
            art_style=art_style,
            child_name=child_name,
            job_name=job_name,
            child_age=child_age,
            child_gender=child_gender,
            job_name_en=job_name_en,
            job_outfit=job_outfit,
        )
    except IllustrationGenerationError as e:
        logger.warning(f"AI 표지 생성 실패, 더미 폴백: {e}")
        return None
