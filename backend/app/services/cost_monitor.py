"""AI API 비용 모니터링 서비스

API 호출 횟수, 토큰 사용량을 로깅한다.
실제 API 호출은 하지 않으며, 로깅만 수행.
"""
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("ai_cost_monitor")


@dataclass
class APICallRecord:
    """단일 API 호출 기록"""
    service: str  # "story", "character", "illustration"
    model: str  # "gpt-4o", "gpt-image-1"
    timestamp: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    image_count: int = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class CostMonitorStats:
    """누적 통계"""
    story_calls: int = 0
    story_tokens: int = 0
    character_calls: int = 0
    character_images: int = 0
    illustration_calls: int = 0
    illustration_images: int = 0
    total_errors: int = 0


class CostMonitor:
    """AI API 비용 모니터링 싱글톤"""

    _instance: Optional["CostMonitor"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._stats = CostMonitorStats()
                cls._instance._records: list[APICallRecord] = []
            return cls._instance

    @property
    def stats(self) -> CostMonitorStats:
        return self._stats

    @property
    def records(self) -> list[APICallRecord]:
        return list(self._records)

    def log_story_call(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """스토리 생성 API 호출 기록"""
        record = APICallRecord(
            service="story",
            model=get_settings().TEXT_MODEL,
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            success=success,
            error=error,
        )
        self._records.append(record)
        self._stats.story_calls += 1
        self._stats.story_tokens += total_tokens
        if not success:
            self._stats.total_errors += 1

        logger.info(
            f"[COST] story call #{self._stats.story_calls} | "
            f"tokens={total_tokens} (prompt={prompt_tokens}, completion={completion_tokens}) | "
            f"success={success}"
        )

    def log_character_call(
        self,
        image_count: int = 1,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """캐릭터 시트 생성 API 호출 기록"""
        record = APICallRecord(
            service="character",
            model=get_settings().IMAGE_MODEL,
            timestamp=datetime.now(timezone.utc).isoformat(),
            image_count=image_count,
            success=success,
            error=error,
        )
        self._records.append(record)
        self._stats.character_calls += 1
        self._stats.character_images += image_count
        if not success:
            self._stats.total_errors += 1

        logger.info(
            f"[COST] character call #{self._stats.character_calls} | "
            f"images={image_count} | success={success}"
        )

    def log_illustration_call(
        self,
        image_count: int = 1,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """일러스트 생성 API 호출 기록"""
        record = APICallRecord(
            service="illustration",
            model=get_settings().IMAGE_MODEL,
            timestamp=datetime.now(timezone.utc).isoformat(),
            image_count=image_count,
            success=success,
            error=error,
        )
        self._records.append(record)
        self._stats.illustration_calls += 1
        self._stats.illustration_images += image_count
        if not success:
            self._stats.total_errors += 1

        logger.info(
            f"[COST] illustration call #{self._stats.illustration_calls} | "
            f"images={image_count} | success={success}"
        )

    def get_summary(self) -> dict:
        """비용 모니터링 요약 반환"""
        return {
            "story": {
                "calls": self._stats.story_calls,
                "total_tokens": self._stats.story_tokens,
            },
            "character": {
                "calls": self._stats.character_calls,
                "total_images": self._stats.character_images,
            },
            "illustration": {
                "calls": self._stats.illustration_calls,
                "total_images": self._stats.illustration_images,
            },
            "total_errors": self._stats.total_errors,
            "total_records": len(self._records),
        }

    def reset(self):
        """통계 초기화 (테스트용)"""
        self._stats = CostMonitorStats()
        self._records.clear()


# 편의 함수
def get_cost_monitor() -> CostMonitor:
    return CostMonitor()
