"""웹훅 수신 엔드포인트 — Book Print API 웹훅 처리

HMAC-SHA256 서명 검증 후 주문 상태 업데이트.
"""
import hashlib
import hmac
import json
import logging
import time
from collections import OrderedDict
from datetime import datetime, timezone

from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.order import Order

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# 웹훅 시크릿 키 — 환경변수에서 로드 (웹훅 등록 시 발급된 secretKey)
settings = get_settings()
WEBHOOK_SECRET: str = settings.WEBHOOK_SECRET

# 중복 이벤트 방지 — 처리된 delivery ID 캐시 (OrderedDict FIFO, 서비스 재시작 시 초기화)
_processed_deliveries: OrderedDict = OrderedDict()
# 캐시 최대 크기 (메모리 보호)
_MAX_DELIVERY_CACHE = 10000

# 타임스탬프 허용 오차 (초) — 5분
TIMESTAMP_TOLERANCE = 300

# 상태 코드 매핑
STATUS_CODE_MAP = {
    "PAID": 20,
    "PDF_READY": 25,
    "CONFIRMED": 30,
    "IN_PRODUCTION": 40,
    "SHIPPED": 50,
    "DELIVERED": 60,
    "CANCELLED": 80,
    "CANCELLED_REFUND": 81,
}


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    timestamp: str,
    secret: str,
    tolerance: int = TIMESTAMP_TOLERANCE,
) -> bool:
    """HMAC-SHA256 서명 검증

    수식: HMAC-SHA256(secretKey, "{timestamp}.{JSON body}")

    Args:
        payload: 요청 body (bytes)
        signature: X-Webhook-Signature 헤더 값 (hex)
        timestamp: X-Webhook-Timestamp 헤더 값 (Unix초)
        secret: 웹훅 secretKey
        tolerance: 타임스탬프 허용 오차 (초, 기본 300)

    Returns:
        서명 유효 여부
    """
    if not signature or not timestamp or not secret:
        return False

    # sha256= 접두사 자동 제거 (SDK 호환)
    if signature.startswith("sha256="):
        signature = signature[7:]

    # 타임스탬프 만료 검증
    try:
        ts = int(timestamp)
        now = int(time.time())
        if abs(now - ts) > tolerance:
            logger.warning(f"웹훅 타임스탬프 만료: {ts} (현재: {now}, 차이: {abs(now - ts)}초)")
            return False
    except (ValueError, TypeError):
        logger.warning(f"웹훅 타임스탬프 파싱 실패: {timestamp}")
        return False

    # HMAC-SHA256 검증
    message = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature)


def _handle_order_paid(db: Session, data: dict):
    """order.paid 이벤트 처리 — 주문 생성 확인"""
    order_uid = data.get("order_uid")
    if not order_uid:
        return

    order = db.query(Order).filter(Order.bookprint_order_uid == order_uid).first()
    if not order:
        logger.warning(f"웹훅 order.paid: 주문 미발견 ({order_uid})")
        return

    # PAID 상태 확인 (이미 PAID이면 변경 없음)
    if order.status_code <= 20:
        order.status = "PAID"
        order.status_code = 20
        order.updated_at = datetime.now(timezone.utc)
        db.commit()

    logger.info(f"웹훅 order.paid 처리 완료: {order_uid}")


def _handle_order_confirmed(db: Session, data: dict):
    """order.confirmed 이벤트 처리 — 제작 확정"""
    order_uid = data.get("order_uid")
    if not order_uid:
        return

    order = db.query(Order).filter(Order.bookprint_order_uid == order_uid).first()
    if not order:
        logger.warning(f"웹훅 order.confirmed: 주문 미발견 ({order_uid})")
        return

    # 상태 역행 방지 — 이미 CONFIRMED(30) 이상이면 무시
    if order.status_code >= 30:
        logger.info(f"웹훅 order.confirmed 무시 (현재 상태: {order.status}({order.status_code}) >= CONFIRMED(30))")
        return

    order.status = "CONFIRMED"
    order.status_code = 30
    order.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"웹훅 order.confirmed 처리 완료: {order_uid}")


def _handle_order_status_changed(db: Session, data: dict):
    """order.status_changed 이벤트 처리 — 범용 상태 변경"""
    order_uid = data.get("order_uid")
    new_status = data.get("newStatus")
    if not order_uid or not new_status:
        return

    order = db.query(Order).filter(Order.bookprint_order_uid == order_uid).first()
    if not order:
        logger.warning(f"웹훅 order.status_changed: 주문 미발견 ({order_uid})")
        return

    # 상태 코드 매핑
    status_code = STATUS_CODE_MAP.get(new_status, order.status_code)

    # 상태 역행 방지 — CANCELLED(80+)은 어떤 상태에서든 전이 가능
    if status_code < 80 and order.status_code >= status_code:
        logger.info(
            f"웹훅 order.status_changed 무시 (현재: {order.status}({order.status_code}) >= {new_status}({status_code}))"
        )
        return

    order.status = new_status
    order.status_code = status_code
    order.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"웹훅 order.status_changed 처리 완료: {order_uid} -> {new_status} ({status_code})")


def _handle_order_shipped(db: Session, data: dict):
    """order.shipped 이벤트 처리 — 배송 정보 업데이트"""
    order_uid = data.get("order_uid")
    if not order_uid:
        return

    order = db.query(Order).filter(Order.bookprint_order_uid == order_uid).first()
    if not order:
        logger.warning(f"웹훅 order.shipped: 주문 미발견 ({order_uid})")
        return

    # 상태 역행 방지 — 이미 SHIPPED(50) 이상이면 무시
    if order.status_code >= 50:
        logger.info(f"웹훅 order.shipped 무시 (현재 상태: {order.status}({order.status_code}) >= SHIPPED(50))")
        return

    order.status = "SHIPPED"
    order.status_code = 50
    order.tracking_number = data.get("trackingNumber") or data.get("tracking_number")
    order.tracking_carrier = data.get("trackingCarrier") or data.get("tracking_carrier")
    order.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(
        f"웹훅 order.shipped 처리 완료: {order_uid} "
        f"(운송장: {order.tracking_number}, 택배: {order.tracking_carrier})"
    )


def _handle_order_cancelled(db: Session, data: dict):
    """order.cancelled 이벤트 처리 — 주문 취소"""
    order_uid = data.get("order_uid")
    if not order_uid:
        return

    order = db.query(Order).filter(Order.bookprint_order_uid == order_uid).first()
    if not order:
        logger.warning(f"웹훅 order.cancelled: 주문 미발견 ({order_uid})")
        return

    order.status = "CANCELLED"
    order.status_code = 80
    order.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"웹훅 order.cancelled 처리 완료: {order_uid}")


# 이벤트 핸들러 매핑
EVENT_HANDLERS = {
    "order.paid": _handle_order_paid,
    "order.confirmed": _handle_order_confirmed,
    "order.status_changed": _handle_order_status_changed,
    "order.shipped": _handle_order_shipped,
    "order.cancelled": _handle_order_cancelled,
}


@router.post("/webhooks/sweetbook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Book Print API 웹훅 수신 엔드포인트

    - HMAC-SHA256 서명 검증
    - 이벤트별 주문 상태 업데이트
    - 중복 이벤트 감지 (X-Webhook-Delivery)
    - 30초 내 200 응답 반환 (모범 사례 준수)
    """
    # 헤더 추출
    signature = request.headers.get("X-Webhook-Signature", "")
    timestamp = request.headers.get("X-Webhook-Timestamp", "")
    event_type = request.headers.get("X-Webhook-Event", "")
    delivery_id = request.headers.get("X-Webhook-Delivery", "")

    # 원시 body 읽기 (서명 검증용)
    body = await request.body()

    # 서명 검증
    if not verify_webhook_signature(body, signature, timestamp, WEBHOOK_SECRET):
        logger.warning(f"웹훅 서명 검증 실패 (event: {event_type}, delivery: {delivery_id})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="웹훅 서명 검증 실패",
        )

    # 중복 이벤트 감지 (OrderedDict의 key 존재 여부 확인)
    if delivery_id and delivery_id in _processed_deliveries:
        logger.info(f"웹훅 중복 이벤트 무시: {delivery_id}")
        return {"received": True, "duplicate": True}

    # body 파싱
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("웹훅 body 파싱 실패")
        return {"received": True, "error": "invalid_json"}

    data = payload.get("data", {})
    is_test = payload.get("isTest", False)

    logger.info(
        f"웹훅 수신: event={event_type}, delivery={delivery_id}, "
        f"isTest={is_test}, order_uid={data.get('order_uid')}"
    )

    # 이벤트 처리
    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        try:
            handler(db, data)
        except Exception as e:
            logger.error(f"웹훅 이벤트 처리 오류: {event_type} - {e}")
            # 처리 오류에도 200 반환 (재시도 방지 — 로그로 추적)
            return {"received": True, "error": "processing_failed"}
    else:
        logger.warning(f"웹훅 미지원 이벤트: {event_type}")

    # delivery ID 캐시에 추가 (FIFO 순서 보장 — OrderedDict)
    if delivery_id:
        while len(_processed_deliveries) >= _MAX_DELIVERY_CACHE:
            _processed_deliveries.popitem(last=False)  # 가장 오래된 항목 제거
        _processed_deliveries[delivery_id] = True

    return {"received": True}
