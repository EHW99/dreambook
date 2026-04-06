"""태스크 10: Book Print API 연동 + 주문 테스트"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.schemas.order import ShippingInfo, ShippingUpdateRequest, OrderRequest


# === Schema 검증 테스트 (TDD RED → GREEN) ===

class TestShippingInfoValidation:
    """배송지 정보 입력 검증"""

    def test_valid_shipping_info(self):
        """정상 배송지 정보"""
        info = ShippingInfo(
            recipient_name="홍길동",
            recipient_phone="010-1234-5678",
            postal_code="06101",
            address1="서울시 강남구 테헤란로 123",
            address2="4층 401호",
            shipping_memo="부재시 경비실",
        )
        assert info.recipient_name == "홍길동"
        assert info.postal_code == "06101"

    def test_empty_recipient_name_fails(self):
        """수령인 이름 누락"""
        with pytest.raises(Exception):
            ShippingInfo(
                recipient_name="",
                recipient_phone="010-1234-5678",
                postal_code="06101",
                address1="서울시 강남구",
            )

    def test_long_recipient_name_fails(self):
        """수령인 이름 100자 초과"""
        with pytest.raises(Exception):
            ShippingInfo(
                recipient_name="가" * 101,
                recipient_phone="010-1234-5678",
                postal_code="06101",
                address1="서울시 강남구",
            )

    def test_invalid_phone_format(self):
        """잘못된 전화번호 형식"""
        with pytest.raises(Exception):
            ShippingInfo(
                recipient_name="홍길동",
                recipient_phone="1234",
                postal_code="06101",
                address1="서울시 강남구",
            )

    def test_valid_phone_without_dash(self):
        """대시 없는 전화번호"""
        info = ShippingInfo(
            recipient_name="홍길동",
            recipient_phone="01012345678",
            postal_code="06101",
            address1="서울시 강남구",
        )
        assert info.recipient_phone == "01012345678"

    def test_invalid_postal_code(self):
        """잘못된 우편번호"""
        with pytest.raises(Exception):
            ShippingInfo(
                recipient_name="홍길동",
                recipient_phone="010-1234-5678",
                postal_code="1234",  # 4자리
                address1="서울시 강남구",
            )

    def test_empty_address_fails(self):
        """주소 누락"""
        with pytest.raises(Exception):
            ShippingInfo(
                recipient_name="홍길동",
                recipient_phone="010-1234-5678",
                postal_code="06101",
                address1="",
            )

    def test_optional_address2_and_memo(self):
        """상세주소와 메모는 선택사항"""
        info = ShippingInfo(
            recipient_name="홍길동",
            recipient_phone="010-1234-5678",
            postal_code="06101",
            address1="서울시 강남구",
        )
        assert info.address2 is None
        assert info.shipping_memo is None


# === BookPrint Service 테스트 ===

class TestBookPrintService:
    """BookPrintService 단위 테스트 (API 모킹)"""

    @pytest.mark.asyncio
    async def test_get_credit_balance(self):
        """충전금 잔액 조회"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://test")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"balance": 100000, "currency": "KRW", "env": "test"},
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            result = await service.get_credit_balance()
            assert result["balance"] == 100000

    @pytest.mark.asyncio
    async def test_ensure_sufficient_credits_charges_when_zero(self):
        """잔액 0이면 자동 충전"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://test")

        # 잔액 조회 응답 (0원)
        balance_response = MagicMock()
        balance_response.status_code = 200
        balance_response.json.return_value = {
            "success": True,
            "data": {"balance": 0, "currency": "KRW", "env": "test"},
        }

        # 충전 응답
        charge_response = MagicMock()
        charge_response.status_code = 200
        charge_response.json.return_value = {
            "success": True,
            "data": {"balance": 1000000, "currency": "KRW"},
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(side_effect=[balance_response, charge_response])
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            result = await service.ensure_sufficient_credits()
            assert result["balance"] == 1000000

    @pytest.mark.asyncio
    async def test_create_book(self):
        """책 생성 → bookUid 반환"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://test")

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "data": {"bookUid": "bk_test123"},
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            book_uid = await service.create_book("테스트 동화책", "SQUAREBOOK_HC")
            assert book_uid == "bk_test123"

    @pytest.mark.asyncio
    async def test_get_estimate(self):
        """견적 조회"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://test")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "productAmount": 20300,
                "shippingFee": 3500,
                "packagingFee": 500,
                "totalAmount": 24300,
                "paidCreditAmount": 26730,
                "creditBalance": 1000000,
                "creditSufficient": True,
            },
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            result = await service.get_estimate("bk_test123")
            assert result["totalAmount"] == 24300
            assert result["creditSufficient"] is True

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """API 에러 → BookPrintAPIError"""
        from app.services.bookprint import BookPrintService, BookPrintAPIError

        service = BookPrintService(api_key="test_key", base_url="http://test")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "message": "Unauthorized",
            "errors": ["인증 실패"],
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            with pytest.raises(BookPrintAPIError) as exc_info:
                await service.get_credit_balance()
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """타임아웃 처리"""
        import httpx
        from app.services.bookprint import BookPrintService, BookPrintAPIError

        service = BookPrintService(api_key="test_key", base_url="http://test")

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            with pytest.raises(BookPrintAPIError) as exc_info:
                await service.get_credit_balance()
            assert exc_info.value.status_code == 408


# === API 엔드포인트 통합 테스트 ===

class TestOrderEndpoints:
    """주문 API 엔드포인트 테스트"""

    def _create_test_user(self, client):
        """테스트 사용자 생성 + 로그인"""
        client.post("/api/auth/signup", json={
            "email": "order@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "order@test.com",
            "password": "test1234",
        })
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_book_with_pages(self, client, headers, db_session):
        """테스트용 동화책 + 페이지 생성"""
        # 이용권 구매
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]

        # 동화책 생성
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # 필수 정보 입력
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "테스트아이",
            "job_name": "소방관",
            "job_category": "안전",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
            "page_count": 24,
        }, headers=headers)

        # 캐릭터 생성 + 선택
        char_res = client.post(f"/api/books/{book_id}/character", headers=headers)
        char_id = char_res.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=headers)

        # status를 character_confirmed로
        client.patch(f"/api/books/{book_id}", json={
            "status": "character_confirmed",
            "current_step": 6,
        }, headers=headers)

        # 스토리 생성
        client.post(f"/api/books/{book_id}/generate", headers=headers)

        # status를 editing으로
        client.patch(f"/api/books/{book_id}", json={"status": "editing"}, headers=headers)

        return book_id

    def test_estimate_requires_editing_status(self, client, db_session):
        """견적 조회 — editing/completed 상태 필요"""
        headers = self._create_test_user(client)

        # 이용권 구매 + 동화책 생성
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # draft 상태에서 견적 조회 시도 → 실패
        res = client.post(f"/api/books/{book_id}/estimate", headers=headers)
        assert res.status_code == 422

    def test_estimate_returns_price(self, client, db_session):
        """견적 조회 — 정상 응답"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        res = client.post(f"/api/books/{book_id}/estimate", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "total_amount" in data
        assert "shipping_fee" in data
        assert "packaging_fee" in data
        assert data["shipping_fee"] == 3500

    def test_order_requires_editing_status(self, client, db_session):
        """주문 — editing/completed 상태 필요"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        res = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res.status_code == 422

    def test_order_validates_shipping(self, client, db_session):
        """주문 — 배송지 검증"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        # 빈 수령인
        res = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res.status_code == 422

        # 잘못된 전화번호
        res = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "1234",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res.status_code == 422

        # 잘못된 우편번호
        res = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "1234",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res.status_code == 422

    @patch("app.api.orders.BookPrintService")
    def test_order_creates_record(self, MockService, client, db_session):
        """주문 — Book Print API 워크플로우 실행 + DB 기록"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        # BookPrintService 모킹
        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_test123",
            "order_uid": "or_test456",
            "order_status": 20,
            "order_status_display": "결제완료",
            "total_amount": 24300,
            "paid_credit_amount": 26730,
            "estimate": {},
            "order_data": {},
        })
        mock_instance.close = AsyncMock()

        res = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구 테헤란로 123",
                "address2": "4층",
                "shipping_memo": "부재시 경비실",
            }
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "PAID"
        assert data["status_code"] == 20
        assert data["bookprint_order_uid"] == "or_test456"
        assert data["recipient_name"] == "홍길동"

    @patch("app.api.orders.BookPrintService")
    def test_duplicate_order_fails(self, MockService, client, db_session):
        """중복 주문 방지"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_test123",
            "order_uid": "or_test456",
            "order_status": 20,
            "order_status_display": "결제완료",
            "total_amount": 24300,
            "paid_credit_amount": 26730,
            "estimate": {},
            "order_data": {},
        })
        mock_instance.close = AsyncMock()

        # 첫 주문 성공
        res1 = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res1.status_code == 200

        # 두 번째 주문 실패
        res2 = client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)
        assert res2.status_code == 400

    def test_list_orders_empty(self, client, db_session):
        """주문 목록 — 빈 상태"""
        headers = self._create_test_user(client)
        res = client.get("/api/orders", headers=headers)
        assert res.status_code == 200
        assert res.json() == []

    @patch("app.api.orders.BookPrintService")
    def test_list_and_get_order(self, MockService, client, db_session):
        """주문 목록 + 상세 조회"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_t1",
            "order_uid": "or_t1",
            "order_status": 20,
            "order_status_display": "결제완료",
            "total_amount": 10000,
            "paid_credit_amount": 11000,
            "estimate": {},
            "order_data": {},
        })
        mock_instance.close = AsyncMock()

        client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "김영희",
                "recipient_phone": "010-9999-8888",
                "postal_code": "12345",
                "address1": "부산시 해운대구",
            }
        }, headers=headers)

        # 목록 조회
        res = client.get("/api/orders", headers=headers)
        assert res.status_code == 200
        orders = res.json()
        assert len(orders) == 1
        assert orders[0]["recipient_name"] == "김영희"

        # 상세 조회
        order_id = orders[0]["id"]
        res = client.get(f"/api/orders/{order_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["bookprint_order_uid"] == "or_t1"

    @patch("app.api.orders.BookPrintService")
    def test_cancel_order(self, MockService, client, db_session):
        """주문 취소 (PAID 상태)"""
        headers = self._create_test_user(client)
        book_id = self._create_book_with_pages(client, headers, db_session)

        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_t1", "order_uid": "or_t1", "order_status": 20,
            "order_status_display": "결제완료", "total_amount": 10000,
            "paid_credit_amount": 11000, "estimate": {}, "order_data": {},
        })
        mock_instance.cancel_order = AsyncMock(return_value={})
        mock_instance.close = AsyncMock()

        client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)

        orders = client.get("/api/orders", headers=headers).json()
        order_id = orders[0]["id"]

        res = client.post(f"/api/orders/{order_id}/cancel", headers=headers)
        assert res.status_code == 200

        # 상태 확인
        order = client.get(f"/api/orders/{order_id}", headers=headers).json()
        assert order["status"] == "CANCELLED_REFUND"
        assert order["status_code"] == 81

    def test_order_auth_required(self, client, db_session):
        """인증 없이 주문 API 접근 불가"""
        res = client.get("/api/orders")
        assert res.status_code in (401, 403)

    def test_order_not_found(self, client, db_session):
        """존재하지 않는 주문 조회"""
        headers = self._create_test_user(client)
        res = client.get("/api/orders/9999", headers=headers)
        assert res.status_code == 404


# === 로컬 견적 계산 테스트 ===

class TestLocalEstimate:
    """로컬 견적 계산 로직"""

    def test_squarebook_24p_price(self):
        """SQUAREBOOK_HC 24페이지 기본 가격"""
        from app.api.orders import _calculate_local_estimate
        mock_book = MagicMock()
        mock_book.page_count = 24
        mock_book.book_spec_uid = "SQUAREBOOK_HC"

        result = _calculate_local_estimate(mock_book)
        assert result["productAmount"] == 19800
        assert result["shippingFee"] == 3500
        assert result["packagingFee"] == 500

    def test_squarebook_40p_price(self):
        """SQUAREBOOK_HC 40페이지 추가 비용"""
        from app.api.orders import _calculate_local_estimate
        mock_book = MagicMock()
        mock_book.page_count = 40
        mock_book.book_spec_uid = "SQUAREBOOK_HC"

        result = _calculate_local_estimate(mock_book)
        # 19800 + (40-24)/2 * 500 = 19800 + 4000 = 23800
        assert result["productAmount"] == 23800

    def test_a4_softcover_price(self):
        """PHOTOBOOK_A4_SC 가격"""
        from app.api.orders import _calculate_local_estimate
        mock_book = MagicMock()
        mock_book.page_count = 24
        mock_book.book_spec_uid = "PHOTOBOOK_A4_SC"

        result = _calculate_local_estimate(mock_book)
        assert result["productAmount"] == 15800


# === ShippingUpdateRequest 스키마 테스트 ===

class TestShippingUpdateRequestValidation:
    """배송지 변경 스키마 (부분 업데이트) 테스트"""

    def test_partial_update_name_only(self):
        """이름만 변경"""
        req = ShippingUpdateRequest(recipient_name="김철수")
        assert req.recipient_name == "김철수"
        assert req.recipient_phone is None
        assert req.postal_code is None

    def test_partial_update_phone_only(self):
        """전화번호만 변경"""
        req = ShippingUpdateRequest(recipient_phone="010-9999-0000")
        assert req.recipient_phone == "010-9999-0000"
        assert req.recipient_name is None

    def test_all_fields_optional(self):
        """모든 필드 비어도 생성 가능"""
        req = ShippingUpdateRequest()
        assert req.recipient_name is None
        assert req.recipient_phone is None

    def test_invalid_phone_rejected(self):
        """잘못된 전화번호 검증"""
        with pytest.raises(Exception):
            ShippingUpdateRequest(recipient_phone="1234")

    def test_invalid_postal_code_rejected(self):
        """잘못된 우편번호 검증"""
        with pytest.raises(Exception):
            ShippingUpdateRequest(postal_code="123")


# === 배송지 변경 API 테스트 ===

class TestUpdateShippingEndpoint:
    """PATCH /orders/:id/shipping 테스트"""

    def _create_test_user(self, client):
        """테스트 사용자 생성 + 로그인"""
        client.post("/api/auth/signup", json={
            "email": "shipping@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "shipping@test.com",
            "password": "test1234",
        })
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_order(self, client, headers, db_session, MockService):
        """테스트용 주문 생성"""
        # 이용권 구매
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]

        # 동화책 생성
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # 필수 정보 입력
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "테스트아이",
            "job_name": "소방관",
            "job_category": "안전",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
            "page_count": 24,
        }, headers=headers)

        # 캐릭터 생성 + 선택
        char_res = client.post(f"/api/books/{book_id}/character", headers=headers)
        char_id = char_res.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=headers)
        client.patch(f"/api/books/{book_id}", json={
            "status": "character_confirmed",
            "current_step": 6,
        }, headers=headers)

        # 스토리 생성
        client.post(f"/api/books/{book_id}/generate", headers=headers)
        client.patch(f"/api/books/{book_id}", json={"status": "editing"}, headers=headers)

        # BookPrintService 모킹
        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_ship1", "order_uid": "or_ship1", "order_status": 20,
            "order_status_display": "결제완료", "total_amount": 10000,
            "paid_credit_amount": 11000, "estimate": {}, "order_data": {},
        })
        mock_instance.update_shipping = AsyncMock(return_value={})
        mock_instance.close = AsyncMock()

        # 주문 생성
        client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)

        orders = client.get("/api/orders", headers=headers).json()
        return orders[0]["id"]

    @patch("app.api.orders.BookPrintService")
    def test_update_shipping_success(self, MockService, client, db_session):
        """정상 배송지 변경 (전체 필드)"""
        headers = self._create_test_user(client)
        order_id = self._create_order(client, headers, db_session, MockService)

        # 배송지 변경 모킹 재설정
        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.update_shipping = AsyncMock(return_value={})
        mock_instance.close = AsyncMock()

        res = client.patch(f"/api/orders/{order_id}/shipping", json={
            "recipient_name": "김영희",
            "recipient_phone": "010-9999-8888",
            "postal_code": "12345",
            "address1": "부산시 해운대구",
            "address2": "5층",
            "shipping_memo": "문 앞에 놓아주세요",
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["recipient_name"] == "김영희"
        assert data["recipient_phone"] == "010-9999-8888"
        assert data["postal_code"] == "12345"
        assert data["address1"] == "부산시 해운대구"
        assert data["address2"] == "5층"
        assert data["shipping_memo"] == "문 앞에 놓아주세요"

    @patch("app.api.orders.BookPrintService")
    def test_update_shipping_partial(self, MockService, client, db_session):
        """부분 배송지 변경 (이름만)"""
        headers = self._create_test_user(client)
        order_id = self._create_order(client, headers, db_session, MockService)

        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.update_shipping = AsyncMock(return_value={})
        mock_instance.close = AsyncMock()

        res = client.patch(f"/api/orders/{order_id}/shipping", json={
            "recipient_name": "박민수",
        }, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["recipient_name"] == "박민수"
        # 기존 값 유지
        assert data["postal_code"] == "06101"
        assert data["address1"] == "서울시 강남구"

    @patch("app.api.orders.BookPrintService")
    def test_update_shipping_wrong_status(self, MockService, client, db_session):
        """IN_PRODUCTION 상태에서 배송지 변경 시도 → 400"""
        headers = self._create_test_user(client)
        order_id = self._create_order(client, headers, db_session, MockService)

        # 상태를 IN_PRODUCTION(40)으로 변경
        from app.models.order import Order
        order = db_session.query(Order).filter(Order.id == order_id).first()
        order.status = "IN_PRODUCTION"
        order.status_code = 40
        db_session.commit()

        res = client.patch(f"/api/orders/{order_id}/shipping", json={
            "recipient_name": "박민수",
        }, headers=headers)
        assert res.status_code == 400

    @patch("app.api.orders.BookPrintService")
    def test_update_shipping_other_user(self, MockService, client, db_session):
        """타인 주문 배송지 변경 시도 → 403"""
        headers = self._create_test_user(client)
        order_id = self._create_order(client, headers, db_session, MockService)

        # 다른 사용자 생성
        client.post("/api/auth/signup", json={
            "email": "other@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        other_res = client.post("/api/auth/login", json={
            "email": "other@test.com",
            "password": "test1234",
        })
        other_headers = {"Authorization": f"Bearer {other_res.json()['access_token']}"}

        res = client.patch(f"/api/orders/{order_id}/shipping", json={
            "recipient_name": "해커",
        }, headers=other_headers)
        assert res.status_code == 403

    def test_update_shipping_no_auth(self, client, db_session):
        """인증 없이 배송지 변경 시도"""
        res = client.patch("/api/orders/1/shipping", json={
            "recipient_name": "홍길동",
        })
        assert res.status_code in (401, 403)


# === Rate Limit 재시도 테스트 ===

class TestRateLimitRetry:
    """429 Rate Limit 재시도 로직 테스트"""

    @pytest.mark.asyncio
    async def test_429_retries_with_retry_after(self):
        """429 응답 시 Retry-After 헤더 기반 재시도"""
        from app.services.bookprint import BookPrintService

        service = BookPrintService(api_key="test_key", base_url="http://test")

        # 첫 요청: 429, 두 번째: 200
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "1"}

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "success": True,
            "data": {"balance": 100000},
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(side_effect=[rate_limit_response, success_response])
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            with patch("app.services.bookprint.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await service.get_credit_balance()
                assert result["balance"] == 100000
                mock_sleep.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_429_max_retries_exceeded(self):
        """429 응답 3번 연속 → 최대 재시도 초과 시 에러"""
        from app.services.bookprint import BookPrintService, BookPrintAPIError

        service = BookPrintService(api_key="test_key", base_url="http://test")

        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "1"}
        rate_limit_response.json.return_value = {
            "success": False,
            "message": "Too Many Requests",
        }

        with patch.object(service, '_get_client') as mock_client_fn:
            mock_client = AsyncMock()
            mock_client.request = AsyncMock(return_value=rate_limit_response)
            mock_client.is_closed = False
            mock_client_fn.return_value = mock_client

            with patch("app.services.bookprint.asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(BookPrintAPIError) as exc_info:
                    await service.get_credit_balance()
                assert exc_info.value.status_code == 429


# === 페이지 수 검증 + 내지 삽입 실패 테스트 ===

class TestWorkflowValidation:
    """워크플로우 검증 테스트"""

    @pytest.mark.asyncio
    async def test_page_count_out_of_range(self):
        """페이지 수가 판형 범위 밖이면 에러"""
        from app.services.bookprint import BookPrintService, BookPrintAPIError

        service = BookPrintService(api_key="test_key", base_url="http://test")

        # 모든 API 호출 모킹
        service.ensure_sufficient_credits = AsyncMock()
        service.create_book = AsyncMock(return_value="bk_test")
        service.upload_photo = AsyncMock(return_value="file_test.png")
        service.get_templates = AsyncMock(side_effect=[
            [{"templateUid": "tpl_cover"}],  # cover
            [{"templateUid": "tpl_content"}],  # content
        ])
        service.create_cover = AsyncMock()
        service.insert_content = AsyncMock()

        # 10페이지 (SQUAREBOOK_HC 최소 24페이지) — 범위 밖
        pages_data = [{"text": f"page {i}", "image_path": ""} for i in range(10)]

        with pytest.raises(BookPrintAPIError, match="페이지 수.*판형 제약"):
            await service.execute_order_workflow(
                title="테스트",
                book_spec_uid="SQUAREBOOK_HC",
                pages_data=pages_data,
                cover_image_path=None,
                shipping={"recipientName": "홍길동", "address1": "서울"},
            )

    @pytest.mark.asyncio
    async def test_content_insert_failure_aborts_workflow(self):
        """내지 삽입 실패 시 워크플로우 중단"""
        from app.services.bookprint import BookPrintService, BookPrintAPIError

        service = BookPrintService(api_key="test_key", base_url="http://test")

        service.ensure_sufficient_credits = AsyncMock()
        service.create_book = AsyncMock(return_value="bk_test")
        service.upload_photo = AsyncMock(return_value="file_test.png")
        service.get_templates = AsyncMock(side_effect=[
            [{"templateUid": "tpl_cover"}],
            [{"templateUid": "tpl_content"}],
        ])
        service.create_cover = AsyncMock()
        # 내지 삽입 실패
        service.insert_content = AsyncMock(
            side_effect=BookPrintAPIError("서버 오류", status_code=500)
        )
        service.finalize_book = AsyncMock()  # 이건 호출되면 안됨

        pages_data = [{"text": f"page {i}", "image_path": "", "page_type": "story", "page_number": i} for i in range(24)]

        with pytest.raises(BookPrintAPIError, match="내지 삽입 실패"):
            await service.execute_order_workflow(
                title="테스트",
                book_spec_uid="SQUAREBOOK_HC",
                pages_data=pages_data,
                cover_image_path=None,
                shipping={"recipientName": "홍길동", "address1": "서울"},
            )

        # finalize_book이 호출되지 않았는지 확인
        service.finalize_book.assert_not_called()


# === 취소 불가 상태 + 타인 주문 취소 테스트 ===

class TestCancelEdgeCases:
    """주문 취소 엣지 케이스"""

    def _create_test_user(self, client):
        client.post("/api/auth/signup", json={
            "email": "cancel@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "cancel@test.com",
            "password": "test1234",
        })
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def _create_order_helper(self, client, headers, db_session, MockService):
        """테스트용 주문 생성 (취소 테스트용)"""
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "테스트아이", "job_name": "소방관", "job_category": "안전",
            "story_style": "dreaming_today", "art_style": "watercolor", "page_count": 24,
        }, headers=headers)
        char_res = client.post(f"/api/books/{book_id}/character", headers=headers)
        char_id = char_res.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=headers)
        client.patch(f"/api/books/{book_id}", json={"status": "character_confirmed", "current_step": 6}, headers=headers)
        client.post(f"/api/books/{book_id}/generate", headers=headers)
        client.patch(f"/api/books/{book_id}", json={"status": "editing"}, headers=headers)

        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_c1", "order_uid": "or_c1", "order_status": 20,
            "order_status_display": "결제완료", "total_amount": 10000,
            "paid_credit_amount": 11000, "estimate": {}, "order_data": {},
        })
        mock_instance.cancel_order = AsyncMock(return_value={})
        mock_instance.close = AsyncMock()

        client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동", "recipient_phone": "010-1234-5678",
                "postal_code": "06101", "address1": "서울시 강남구",
            }
        }, headers=headers)
        orders = client.get("/api/orders", headers=headers).json()
        return orders[0]["id"]

    @patch("app.api.orders.BookPrintService")
    def test_cancel_in_production_fails(self, MockService, client, db_session):
        """IN_PRODUCTION 상태에서 취소 시도 → 400"""
        headers = self._create_test_user(client)
        order_id = self._create_order_helper(client, headers, db_session, MockService)

        from app.models.order import Order
        order = db_session.query(Order).filter(Order.id == order_id).first()
        order.status = "IN_PRODUCTION"
        order.status_code = 40
        db_session.commit()

        res = client.post(f"/api/orders/{order_id}/cancel", headers=headers)
        assert res.status_code == 400

    @patch("app.api.orders.BookPrintService")
    def test_cancel_other_user_order_fails(self, MockService, client, db_session):
        """타인 주문 취소 시도 → 403"""
        headers = self._create_test_user(client)
        order_id = self._create_order_helper(client, headers, db_session, MockService)

        # 다른 사용자 생성
        client.post("/api/auth/signup", json={"email": "other_cancel@test.com", "password": "test1234", "name": "테스트", "phone": "01012345678"})
        other_res = client.post("/api/auth/login", json={"email": "other_cancel@test.com", "password": "test1234"})
        other_headers = {"Authorization": f"Bearer {other_res.json()['access_token']}"}

        res = client.post(f"/api/orders/{order_id}/cancel", headers=other_headers)
        assert res.status_code == 403


# === 태스크 11: 내 책장 + 주문 내역 관련 추가 테스트 ===

class TestBookshelfEndpoints:
    """태스크 11: 내 책장 API 테스트"""

    def _create_test_user(self, client):
        client.post("/api/auth/signup", json={
            "email": "bookshelf@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "bookshelf@test.com",
            "password": "test1234",
        })
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_books_list_returns_art_style(self, client, db_session):
        """GET /api/books — art_style 필드 포함 확인"""
        headers = self._create_test_user(client)

        # 이용권 구매 + 동화책 생성
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # art_style 설정
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "민지",
            "art_style": "watercolor",
        }, headers=headers)

        # 목록 조회
        res = client.get("/api/books", headers=headers)
        assert res.status_code == 200
        books = res.json()
        assert len(books) == 1
        assert books[0]["art_style"] == "watercolor"
        assert "updated_at" in books[0]

    def test_books_list_returns_updated_at(self, client, db_session):
        """GET /api/books — updated_at 필드 포함 확인"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)

        res = client.get("/api/books", headers=headers)
        assert res.status_code == 200
        books = res.json()
        assert len(books) == 1
        assert "updated_at" in books[0]
        assert books[0]["updated_at"] is not None

    def test_delete_draft_book(self, client, db_session):
        """작성중 동화책 삭제 가능"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        res = client.delete(f"/api/books/{book_id}", headers=headers)
        assert res.status_code == 200

        # 목록에서 제거됨
        res = client.get("/api/books", headers=headers)
        assert len(res.json()) == 0

    def test_delete_completed_book_fails(self, client, db_session):
        """완성된 동화책은 삭제 불가"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # 상태를 completed로 변경
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "민지",
            "status": "completed",
        }, headers=headers)

        res = client.delete(f"/api/books/{book_id}", headers=headers)
        assert res.status_code == 400

    def test_delete_character_confirmed_book(self, client, db_session):
        """character_confirmed 상태 동화책도 삭제 가능 (작성중에 해당)"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # 상태를 character_confirmed로 변경
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "민지",
            "status": "character_confirmed",
        }, headers=headers)

        res = client.delete(f"/api/books/{book_id}", headers=headers)
        assert res.status_code == 200

        # 목록에서 제거됨
        res = client.get("/api/books", headers=headers)
        assert len(res.json()) == 0

    def test_delete_generating_book_fails(self, client, db_session):
        """generating 상태 동화책은 삭제 불가"""
        headers = self._create_test_user(client)

        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        # 상태를 generating으로 변경
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "민지",
            "status": "generating",
        }, headers=headers)

        res = client.delete(f"/api/books/{book_id}", headers=headers)
        assert res.status_code == 400

    def test_empty_bookshelf(self, client, db_session):
        """빈 책장 목록"""
        headers = self._create_test_user(client)
        res = client.get("/api/books", headers=headers)
        assert res.status_code == 200
        assert res.json() == []


class TestOrderListBookTitle:
    """태스크 11: 주문 목록에 book_title 포함 테스트"""

    def _create_test_user(self, client):
        client.post("/api/auth/signup", json={
            "email": "ordertitle@test.com",
            "password": "test1234",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "ordertitle@test.com",
            "password": "test1234",
        })
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    @patch("app.api.orders.BookPrintService")
    def test_order_list_includes_book_title(self, MockService, client, db_session):
        """GET /api/orders — book_title 필드 포함"""
        headers = self._create_test_user(client)

        # 동화책 생성 (풀 워크플로우)
        client.post("/api/vouchers/purchase", json={"voucher_type": "story_and_print"}, headers=headers)
        vouchers_res = client.get("/api/vouchers", headers=headers)
        voucher_id = vouchers_res.json()[0]["id"]
        book_res = client.post("/api/books", json={"voucher_id": voucher_id}, headers=headers)
        book_id = book_res.json()["id"]

        client.patch(f"/api/books/{book_id}", json={
            "child_name": "테스트아이",
            "job_name": "소방관",
            "job_category": "안전",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
            "page_count": 24,
            "title": "용감한 소방관 테스트아이",
        }, headers=headers)

        char_res = client.post(f"/api/books/{book_id}/character", headers=headers)
        char_id = char_res.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=headers)
        client.patch(f"/api/books/{book_id}", json={
            "status": "character_confirmed", "current_step": 6,
        }, headers=headers)
        client.post(f"/api/books/{book_id}/generate", headers=headers)
        client.patch(f"/api/books/{book_id}", json={"status": "editing"}, headers=headers)

        # 주문 생성
        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        mock_instance.execute_order_workflow = AsyncMock(return_value={
            "book_uid": "bk_title1", "order_uid": "or_title1", "order_status": 20,
            "order_status_display": "결제완료", "total_amount": 10000,
            "paid_credit_amount": 11000, "estimate": {}, "order_data": {},
        })
        mock_instance.close = AsyncMock()

        client.post(f"/api/books/{book_id}/order", json={
            "shipping": {
                "recipient_name": "홍길동",
                "recipient_phone": "010-1234-5678",
                "postal_code": "06101",
                "address1": "서울시 강남구",
            }
        }, headers=headers)

        # 주문 목록에 book_title 포함 확인
        res = client.get("/api/orders", headers=headers)
        assert res.status_code == 200
        orders = res.json()
        assert len(orders) == 1
        assert "book_title" in orders[0]
        # generate에서 자동 생성된 제목이 들어감
        assert orders[0]["book_title"] is not None
        assert len(orders[0]["book_title"]) > 0
