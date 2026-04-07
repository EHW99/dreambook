"""이미지 API 공통 유틸리티

- 429 Rate Limit 재시도 (exponential backoff)
- 인풋 이미지 리사이즈 (1024×1024 이하로)
"""
import io
import logging
import time
from PIL import Image

logger = logging.getLogger(__name__)

MAX_INPUT_SIZE = 1024  # 인풋 이미지 최대 변 길이


def resize_image_for_api(file_path: str) -> io.BytesIO:
    """이미지를 API 전송용으로 리사이즈한다.

    긴 변이 MAX_INPUT_SIZE(1024)를 초과하면 비율 유지하며 축소.
    이미 작으면 그대로 반환.
    PNG로 변환하여 BytesIO 반환.
    """
    img = Image.open(file_path)
    w, h = img.size

    if max(w, h) > MAX_INPUT_SIZE:
        ratio = MAX_INPUT_SIZE / max(w, h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        logger.info(f"[resize] {w}×{h} → {new_w}×{new_h}")

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    buf = io.BytesIO()
    buf.name = "image.png"
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def call_with_retry(fn, max_retries: int = 3, base_wait: float = 15.0):
    """429 Rate Limit 발생 시 재시도하는 래퍼.

    Args:
        fn: 호출할 함수 (lambda 또는 callable)
        max_retries: 최대 재시도 횟수
        base_wait: 기본 대기 시간 (초)

    Returns:
        fn()의 반환값

    Raises:
        마지막 시도에서 발생한 예외
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                last_error = e
                if attempt < max_retries:
                    wait = base_wait * (attempt + 1)
                    logger.warning(f"[retry] Rate limit 도달, {wait:.0f}초 후 재시도 ({attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
            raise
    raise last_error  # type: ignore
