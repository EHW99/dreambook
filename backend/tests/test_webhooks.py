"""웹훅 수신 + 주문 상태 추적 테스트 (태스크 12)"""
import hashlib
import hmac
import json
import time
import uuid
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSessionLocal
from app.models.user import User
from app.models.book import Book
from app.models.order import Order
from app.services.auth import hash_password, create_access_token


def _create_test_user(db) -> User:
    """테스트용 사용자 생성"""
    user = User(
        email="webhook_test@example.com",
        password_hash=hash_password("password123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_test_book(db, user_id: int) -> Book:
    """테스트용 동화책 생성"""
    book = Book(
        user_id=user_id,
        child_name="테스트아이",
        status="completed",
        title="테스트 동화책",
        book_spec_uid="SQUAREBOOK_HC",
        page_count=24,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def _create_test_order(db, user_id: int, book_id: int, bookprint_order_uid: str = "ord_test123") -> Order:
    """테스트용 주문 생성"""
    order = Order(
        user_id=user_id,
        book_id=book_id,
        bookprint_order_uid=bookprint_order_uid,
        status="PAID",
        status_code=20,
        recipient_name="홍길동",
        recipient_phone="010-1234-5678",
        postal_code="12345",
        address1="서울시 강남구",
        total_amount=23800,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def _generate_webhook_signature(payload: bytes, secret: str, timestamp: str) -> str:
    """HMAC-SHA256 서명 생성 — 수식: HMAC-SHA256(secretKey, "{timestamp}.{JSON body}")"""
    message = f"{timestamp}.".encode() + payload
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


WEBHOOK_SECRET = "whsk_test_secret_key_12345"


class TestWebhookSignatureVerification:
    """HMAC-SHA256 서명 검증 테스트"""

    def test_valid_signature_passes(self, client, db_session):
        """유효한 서명이면 200 응답"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id)

        payload = json.dumps({
            "event": "order.paid",
            "data": {
                "order_uid": order.bookprint_order_uid,
                "totalCredits": 23800,
            },
            "isTest": True,
        }).encode()

        timestamp = str(int(time.time()))
        signature = _generate_webhook_signature(payload, WEBHOOK_SECRET, timestamp)

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            response = client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": "order.paid",
                    "X-Webhook-Delivery": "wh_test_001",
                },
            )

        assert response.status_code == 200
        assert response.json()["received"] is True

    def test_invalid_signature_rejected(self, client, db_session):
        """잘못된 서명이면 401 응답"""
        payload = json.dumps({
            "event": "order.paid",
            "data": {"order_uid": "ord_test123"},
        }).encode()

        timestamp = str(int(time.time()))

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            response = client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": "invalid_signature_abc123",
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": "order.paid",
                    "X-Webhook-Delivery": "wh_test_002",
                },
            )

        assert response.status_code == 401

    def test_missing_signature_rejected(self, client, db_session):
        """서명 헤더 없으면 401 응답"""
        payload = json.dumps({
            "event": "order.paid",
            "data": {"order_uid": "ord_test123"},
        }).encode()

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            response = client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Event": "order.paid",
                },
            )

        assert response.status_code == 401

    def test_expired_timestamp_rejected(self, client, db_session):
        """타임스탬프가 5분 넘게 오래된 경우 401"""
        payload = json.dumps({
            "event": "order.paid",
            "data": {"order_uid": "ord_test123"},
        }).encode()

        # 10분 전 타임스탬프
        old_timestamp = str(int(time.time()) - 600)
        signature = _generate_webhook_signature(payload, WEBHOOK_SECRET, old_timestamp)

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            response = client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": old_timestamp,
                    "X-Webhook-Event": "order.paid",
                    "X-Webhook-Delivery": "wh_test_003",
                },
            )

        assert response.status_code == 401


class TestWebhookEventHandling:
    """웹훅 이벤트별 처리 테스트"""

    def _send_webhook(self, client, event_type: str, data: dict, delivery_id: str | None = None):
        """헬퍼: 유효한 서명으로 웹훅 전송"""
        if delivery_id is None:
            delivery_id = f"wh_{uuid.uuid4().hex[:12]}"

        payload = json.dumps({
            "event": event_type,
            "data": data,
            "isTest": True,
        }).encode()

        timestamp = str(int(time.time()))
        signature = _generate_webhook_signature(payload, WEBHOOK_SECRET, timestamp)

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            return client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": event_type,
                    "X-Webhook-Delivery": delivery_id,
                },
            )

    def test_order_paid_event(self, client, db_session):
        """order.paid 이벤트 — 주문 상태 PAID 확인"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_paid_test")

        response = self._send_webhook(client, "order.paid", {
            "order_uid": "ord_paid_test",
            "totalCredits": 23800,
            "shippingAddress": {"recipientName": "홍길동"},
        })

        assert response.status_code == 200
        # 상태는 PAID로 유지
        db_session.refresh(order)
        assert order.status == "PAID"
        assert order.status_code == 20

    def test_order_confirmed_event(self, client, db_session):
        """order.confirmed 이벤트 — 주문 상태 CONFIRMED 업데이트"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_confirm_test")

        response = self._send_webhook(client, "order.confirmed", {
            "order_uid": "ord_confirm_test",
            "confirmedAt": "2026-04-03T10:00:00Z",
            "estimatedShipDate": "2026-04-07",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "CONFIRMED"
        assert order.status_code == 30

    def test_order_status_changed_event(self, client, db_session):
        """order.status_changed 이벤트 — 상태 전이"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_status_test")

        response = self._send_webhook(client, "order.status_changed", {
            "order_uid": "ord_status_test",
            "previousStatus": "PAID",
            "newStatus": "IN_PRODUCTION",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "IN_PRODUCTION"
        assert order.status_code == 40

    def test_order_shipped_event(self, client, db_session):
        """order.shipped 이벤트 — 배송 정보 업데이트"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_ship_test")

        response = self._send_webhook(client, "order.shipped", {
            "order_uid": "ord_ship_test",
            "trackingNumber": "1234567890",
            "trackingCarrier": "HANJIN",
            "shippedAt": "2026-04-07T15:00:00Z",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "SHIPPED"
        assert order.status_code == 50
        assert order.tracking_number == "1234567890"
        assert order.tracking_carrier == "HANJIN"

    def test_order_cancelled_event(self, client, db_session):
        """order.cancelled 이벤트 — 주문 취소 상태"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_cancel_test")

        response = self._send_webhook(client, "order.cancelled", {
            "order_uid": "ord_cancel_test",
            "cancelledAt": "2026-04-03T12:00:00Z",
            "cancelReason": "고객 요청",
            "refundedCredits": 23800,
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "CANCELLED"
        assert order.status_code == 80

    def test_unknown_order_uid_ignored(self, client, db_session):
        """존재하지 않는 주문 UID — 200 응답 (무시)"""
        response = self._send_webhook(client, "order.paid", {
            "order_uid": "ord_nonexistent_999",
        })
        # 웹훅은 항상 200 반환 (재시도 방지)
        assert response.status_code == 200

    def test_duplicate_delivery_id_ignored(self, client, db_session):
        """중복 delivery ID — 멱등성 보장"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_dup_test")

        # 첫 번째 요청
        self._send_webhook(client, "order.confirmed", {
            "order_uid": "ord_dup_test",
            "confirmedAt": "2026-04-03T10:00:00Z",
        }, delivery_id="wh_dup_001")

        db_session.refresh(order)
        assert order.status == "CONFIRMED"

        # 동일한 delivery_id로 다른 이벤트 — 중복 감지로 무시
        self._send_webhook(client, "order.shipped", {
            "order_uid": "ord_dup_test",
            "trackingNumber": "9999999999",
            "trackingCarrier": "CJ",
        }, delivery_id="wh_dup_001")

        db_session.refresh(order)
        # 중복 이벤트이므로 상태 변경 없음
        assert order.status == "CONFIRMED"


class TestWebhookSignatureSha256Prefix:
    """sha256= 접두사 포함 서명 테스트"""

    def test_sha256_prefix_signature_accepted(self, client, db_session):
        """X-Webhook-Signature: sha256=<hex> 형식도 정상 처리"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_sha256_test")

        payload = json.dumps({
            "event": "order.paid",
            "data": {"order_uid": "ord_sha256_test"},
            "isTest": True,
        }).encode()

        timestamp = str(int(time.time()))
        raw_sig = _generate_webhook_signature(payload, WEBHOOK_SECRET, timestamp)
        prefixed_sig = f"sha256={raw_sig}"

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            response = client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": prefixed_sig,
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": "order.paid",
                    "X-Webhook-Delivery": f"wh_sha256_{int(time.time())}",
                },
            )

        assert response.status_code == 200
        assert response.json()["received"] is True


class TestWebhookStateRegressionPrevention:
    """상태 역행 방지 테스트"""

    def _send_webhook(self, client, event_type: str, data: dict, delivery_id: str | None = None):
        if delivery_id is None:
            delivery_id = f"wh_{uuid.uuid4().hex[:12]}"

        payload = json.dumps({
            "event": event_type,
            "data": data,
            "isTest": True,
        }).encode()

        timestamp = str(int(time.time()))
        signature = _generate_webhook_signature(payload, WEBHOOK_SECRET, timestamp)

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            return client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": event_type,
                    "X-Webhook-Delivery": delivery_id,
                },
            )

    def test_shipped_order_ignores_confirmed_event(self, client, db_session):
        """SHIPPED(50) 주문에 order.confirmed 이벤트 → 상태 유지"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_regress_test1")

        # 주문을 SHIPPED 상태로 설정
        order.status = "SHIPPED"
        order.status_code = 50
        db_session.commit()

        response = self._send_webhook(client, "order.confirmed", {
            "order_uid": "ord_regress_test1",
            "confirmedAt": "2026-04-03T10:00:00Z",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "SHIPPED"
        assert order.status_code == 50

    def test_shipped_order_ignores_status_changed_to_lower(self, client, db_session):
        """SHIPPED(50) 주문에 order.status_changed(IN_PRODUCTION=40) → 상태 유지"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_regress_test2")

        order.status = "SHIPPED"
        order.status_code = 50
        db_session.commit()

        response = self._send_webhook(client, "order.status_changed", {
            "order_uid": "ord_regress_test2",
            "previousStatus": "SHIPPED",
            "newStatus": "IN_PRODUCTION",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "SHIPPED"
        assert order.status_code == 50

    def test_cancelled_overrides_any_state(self, client, db_session):
        """CANCELLED(80)은 어떤 상태에서든 전이 가능"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_regress_test3")

        order.status = "SHIPPED"
        order.status_code = 50
        db_session.commit()

        response = self._send_webhook(client, "order.cancelled", {
            "order_uid": "ord_regress_test3",
            "cancelledAt": "2026-04-03T12:00:00Z",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "CANCELLED"
        assert order.status_code == 80

    def test_delivered_order_ignores_shipped_event(self, client, db_session):
        """DELIVERED(60) 주문에 order.shipped 이벤트 → 상태 유지"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_regress_test4")

        order.status = "DELIVERED"
        order.status_code = 60
        db_session.commit()

        response = self._send_webhook(client, "order.shipped", {
            "order_uid": "ord_regress_test4",
            "trackingNumber": "9999",
            "trackingCarrier": "CJ",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "DELIVERED"
        assert order.status_code == 60

    def test_status_changed_cancelled_overrides_shipped(self, client, db_session):
        """order.status_changed로 CANCELLED 전이 — SHIPPED에서도 가능"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_regress_test5")

        order.status = "SHIPPED"
        order.status_code = 50
        db_session.commit()

        response = self._send_webhook(client, "order.status_changed", {
            "order_uid": "ord_regress_test5",
            "previousStatus": "SHIPPED",
            "newStatus": "CANCELLED",
        })

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "CANCELLED"
        assert order.status_code == 80


class TestWebhookSandboxAwareness:
    """Sandbox 환경 인지 테스트"""

    def _send_webhook(self, client, event_type: str, data: dict, is_test: bool = True):
        payload = json.dumps({
            "event": event_type,
            "data": data,
            "isTest": is_test,
        }).encode()

        timestamp = str(int(time.time()))
        signature = _generate_webhook_signature(payload, WEBHOOK_SECRET, timestamp)

        with patch("app.api.webhooks.WEBHOOK_SECRET", WEBHOOK_SECRET):
            return client.post(
                "/api/webhooks/sweetbook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Timestamp": timestamp,
                    "X-Webhook-Event": event_type,
                    "X-Webhook-Delivery": f"wh_sandbox_{int(time.time())}",
                },
            )

    def test_sandbox_paid_no_further_transition(self, client, db_session):
        """Sandbox 환경 — PAID 이후 상태 전이 없음을 인지하고 처리"""
        user = _create_test_user(db_session)
        book = _create_test_book(db_session, user.id)
        order = _create_test_order(db_session, user.id, book.id, "ord_sandbox_test")

        # Sandbox에서 order.paid 이벤트
        response = self._send_webhook(client, "order.paid", {
            "order_uid": "ord_sandbox_test",
            "totalCredits": 100,
        }, is_test=True)

        assert response.status_code == 200
        db_session.refresh(order)
        assert order.status == "PAID"


class TestBookPrintServiceWebhookMethods:
    """BookPrintService의 웹훅 관련 메서드 테스트"""

    @pytest.mark.asyncio
    async def test_register_webhook(self):
        """PUT /webhooks/config 호출 테스트"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://localhost:9999")

        mock_response = {
            "success": True,
            "data": {
                "webhookUrl": "https://example.com/api/webhooks/sweetbook",
                "secretKey": "whsk_new_secret_abc123",
                "events": None,
                "status": "ACTIVE",
            },
        }

        with patch.object(service, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await service.register_webhook("https://example.com/api/webhooks/sweetbook")
            assert result["data"]["secretKey"] == "whsk_new_secret_abc123"

        await service.close()

    @pytest.mark.asyncio
    async def test_send_test_webhook(self):
        """POST /webhooks/test 호출 테스트"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://localhost:9999")

        mock_response = {
            "success": True,
            "data": {
                "deliveryUid": "wh_test_xyz",
                "eventType": "order.paid",
                "status": "SUCCESS",
            },
        }

        with patch.object(service, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await service.send_test_webhook("order.paid")
            assert result["data"]["eventType"] == "order.paid"

        await service.close()

    @pytest.mark.asyncio
    async def test_get_webhook_config(self):
        """GET /webhooks/config 호출 테스트"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://localhost:9999")

        mock_response = {
            "success": True,
            "data": {
                "webhookUrl": "https://example.com/api/webhooks/sweetbook",
                "secretKey": "whsk_new...",
                "events": None,
                "status": "ACTIVE",
            },
        }

        with patch.object(service, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await service.get_webhook_config()
            assert result["data"]["status"] == "ACTIVE"

        await service.close()

    @pytest.mark.asyncio
    async def test_delete_webhook(self):
        """DELETE /webhooks/config 호출 테스트"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://localhost:9999")

        mock_response = {
            "success": True,
            "data": None,
        }

        with patch.object(service, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await service.delete_webhook()
            assert result["success"] is True

        await service.close()

    @pytest.mark.asyncio
    async def test_get_webhook_deliveries(self):
        """GET /webhooks/deliveries 호출 테스트"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://localhost:9999")

        mock_response = {
            "success": True,
            "data": {
                "deliveries": [
                    {
                        "deliveryUid": "wh_del_001",
                        "eventType": "order.paid",
                        "status": "SUCCESS",
                        "createdAt": "2026-04-03T10:00:00Z",
                    },
                    {
                        "deliveryUid": "wh_del_002",
                        "eventType": "order.confirmed",
                        "status": "FAILED",
                        "createdAt": "2026-04-03T11:00:00Z",
                    },
                ],
                "totalCount": 2,
            },
        }

        with patch.object(service, "_request", new_callable=AsyncMock, return_value=mock_response):
            result = await service.get_webhook_deliveries()
            assert result["data"]["totalCount"] == 2
            assert len(result["data"]["deliveries"]) == 2
            assert result["data"]["deliveries"][0]["eventType"] == "order.paid"

        await service.close()
