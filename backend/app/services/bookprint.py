"""Book Print API 연동 서비스

Sandbox 충전금 확인/충전, 책 생성, 사진 업로드, 표지/내지 생성,
최종화, 견적 조회, 주문 생성까지의 전체 워크플로우를 처리한다.
"""
import asyncio
import httpx
import logging
import os
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

# 자동 충전 금액 (Sandbox)
SANDBOX_CHARGE_AMOUNT = 1_000_000

# 판형 UID 하드코딩 (GET /book-specs 403 에러 우회)
BOOK_SPEC_UIDS = {
    "SQUAREBOOK_HC": {
        "name": "정방형 하드커버",
        "width_mm": 243,
        "height_mm": 248,
        "page_min": 24,
        "page_max": 130,
    },
    "PHOTOBOOK_A4_SC": {
        "name": "A4 소프트커버",
        "width_mm": 210,
        "height_mm": 297,
        "page_min": 24,
        "page_max": 130,
    },
    "PHOTOBOOK_A5_SC": {
        "name": "A5 소프트커버",
        "width_mm": 148,
        "height_mm": 210,
        "page_min": 50,
        "page_max": 200,
    },
}


class BookPrintAPIError(Exception):
    """Book Print API 호출 에러"""
    def __init__(self, message: str, status_code: int = 0, detail: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class BookPrintService:
    """Book Print API 연동 서비스 클래스"""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.BOOKPRINT_API_KEY
        self.base_url = (base_url or settings.BOOKPRINT_BASE_URL).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict | None = None,
        data: dict | None = None,
        files: list[tuple] | None = None,
        params: dict | None = None,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """공통 HTTP 요청 메서드 (429 Rate Limit 시 Retry-After 기반 재시도, 최대 2회)"""
        max_retries = 2
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        headers = self._headers()

        if json_data is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                data=data,
                files=files,
                params=params,
            )
        except httpx.TimeoutException:
            raise BookPrintAPIError("Book Print API 요청 시간이 초과되었습니다", status_code=408)
        except httpx.RequestError as e:
            raise BookPrintAPIError(f"Book Print API 연결 실패: {str(e)}", status_code=0)

        # Rate Limit (429) — Retry-After 헤더 기반 재시도
        if response.status_code == 429 and _retry_count < max_retries:
            retry_after = response.headers.get("Retry-After", "1")
            try:
                wait_seconds = int(retry_after)
            except (ValueError, TypeError):
                wait_seconds = 1
            # 안전 상한: 최대 30초 대기
            wait_seconds = min(wait_seconds, 30)
            logger.warning(
                f"Rate Limit (429) — {wait_seconds}초 후 재시도 ({_retry_count + 1}/{max_retries})"
            )
            await asyncio.sleep(wait_seconds)
            return await self._request(
                method, path, json_data=json_data, data=data,
                files=files, params=params, _retry_count=_retry_count + 1,
            )

        if response.status_code == 204:
            return {"success": True}

        try:
            result = response.json()
        except Exception:
            raise BookPrintAPIError(
                f"Book Print API 응답 파싱 실패 (HTTP {response.status_code})",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            message = result.get("message", "알 수 없는 오류")
            errors = result.get("errors", [])
            raise BookPrintAPIError(
                message=f"Book Print API 오류: {message}" + (f" - {errors}" if errors else ""),
                status_code=response.status_code,
                detail=result,
            )

        return result

    # === Credits API ===

    async def get_credit_balance(self) -> dict[str, Any]:
        """충전금 잔액 조회"""
        result = await self._request("GET", "/credits")
        return result.get("data", {})

    async def sandbox_charge(self, amount: int = SANDBOX_CHARGE_AMOUNT, memo: str = "자동 충전") -> dict[str, Any]:
        """Sandbox 테스트 충전"""
        result = await self._request("POST", "/credits/sandbox/charge", json_data={
            "amount": amount,
            "memo": memo,
        })
        return result.get("data", {})

    async def ensure_sufficient_credits(self, required_amount: int = 0) -> dict[str, Any]:
        """충전금 확인 + 부족 시 자동 충전"""
        balance_data = await self.get_credit_balance()
        balance = balance_data.get("balance", 0)

        if balance < required_amount or balance == 0:
            logger.info(f"충전금 부족 (잔액: {balance}원, 필요: {required_amount}원). 자동 충전 시도.")
            charge_data = await self.sandbox_charge()
            return charge_data

        return balance_data

    # === Books API ===

    async def create_book(self, title: str, book_spec_uid: str = "SQUAREBOOK_HC") -> str:
        """Book Print API에서 책 생성 → bookUid 반환"""
        result = await self._request("POST", "/books", json_data={
            "title": title,
            "bookSpecUid": book_spec_uid,
            "creationType": "TEST",
        })
        return result["data"]["bookUid"]

    # === Photos API ===

    async def upload_photo(self, book_uid: str, file_path: str) -> str:
        """사진 업로드 → fileName 반환"""
        if not os.path.exists(file_path):
            raise BookPrintAPIError(f"파일을 찾을 수 없습니다: {file_path}")

        with open(file_path, "rb") as f:
            files = [("file", (os.path.basename(file_path), f, "image/png"))]
            result = await self._request("POST", f"/books/{book_uid}/photos", files=files)

        return result["data"]["fileName"]

    async def upload_photo_from_bytes(self, book_uid: str, filename: str, content: bytes, content_type: str = "image/png") -> str:
        """바이트 데이터로 사진 업로드 → fileName 반환"""
        files = [("file", (filename, content, content_type))]
        result = await self._request("POST", f"/books/{book_uid}/photos", files=files)
        return result["data"]["fileName"]

    # === Templates API ===

    async def get_templates(self, book_spec_uid: str, template_kind: str | None = None) -> list[dict]:
        """템플릿 목록 조회"""
        params: dict[str, Any] = {"bookSpecUid": book_spec_uid}
        if template_kind:
            params["templateKind"] = template_kind
        params["limit"] = 100

        result = await self._request("GET", "/templates", params=params)
        data = result.get("data", {})
        if isinstance(data, dict):
            return data.get("templates", data.get("items", []))
        return data if isinstance(data, list) else []

    # === Covers API ===

    async def create_cover(self, book_uid: str, template_uid: str, parameters: dict, uploaded_file_name: str | None = None) -> dict:
        """표지 생성"""
        form_data: dict[str, Any] = {
            "templateUid": template_uid,
        }

        # parameters에서 이미지 파라미터를 업로드된 파일명으로 대체
        cover_params = dict(parameters)
        if uploaded_file_name:
            # frontPhoto를 업로드된 파일명으로 설정
            cover_params["frontPhoto"] = uploaded_file_name

        import json
        form_data["parameters"] = json.dumps(cover_params)

        # API는 multipart/form-data를 기대 — files 형식으로 전달
        multipart_fields = {k: (None, v) for k, v in form_data.items()}
        result = await self._request("POST", f"/books/{book_uid}/cover", files=multipart_fields)
        return result.get("data", {})

    # === Contents API ===

    async def insert_content(self, book_uid: str, template_uid: str, parameters: dict, break_before: str = "page") -> dict:
        """내지 삽입"""
        import json
        form_data = {
            "templateUid": template_uid,
            "parameters": json.dumps(parameters),
        }

        # API는 multipart/form-data를 기대 — files 형식으로 전달
        multipart_fields = {k: (None, v) for k, v in form_data.items()}
        result = await self._request(
            "POST",
            f"/books/{book_uid}/contents",
            files=multipart_fields,
            params={"breakBefore": break_before},
        )
        return result.get("data", {})

    # === Finalization ===

    async def finalize_book(self, book_uid: str) -> dict:
        """책 최종화"""
        result = await self._request("POST", f"/books/{book_uid}/finalization")
        return result.get("data", {})

    # === Orders API ===

    async def get_estimate(self, book_uid: str, quantity: int = 1) -> dict[str, Any]:
        """견적 조회"""
        result = await self._request("POST", "/orders/estimate", json_data={
            "items": [{"bookUid": book_uid, "quantity": quantity}],
        })
        return result.get("data", {})

    async def create_order(
        self,
        book_uid: str,
        shipping: dict[str, str],
        quantity: int = 1,
        external_ref: str | None = None,
    ) -> dict[str, Any]:
        """주문 생성"""
        order_data: dict[str, Any] = {
            "items": [{"bookUid": book_uid, "quantity": quantity}],
            "shipping": shipping,
        }
        if external_ref:
            order_data["externalRef"] = external_ref

        result = await self._request("POST", "/orders", json_data=order_data)
        return result.get("data", {})

    async def cancel_order(self, order_uid: str, reason: str = "고객 요청") -> dict:
        """주문 취소"""
        result = await self._request("POST", f"/orders/{order_uid}/cancel", json_data={
            "cancelReason": reason,
        })
        return result.get("data", {})

    async def update_shipping(self, order_uid: str, shipping: dict[str, str]) -> dict:
        """배송지 변경"""
        result = await self._request("PATCH", f"/orders/{order_uid}/shipping", json_data=shipping)
        return result.get("data", {})

    # === Webhooks API ===

    async def register_webhook(
        self,
        webhook_url: str,
        events: list[str] | None = None,
        description: str = "꿈꾸는 나 주문 알림",
    ) -> dict[str, Any]:
        """웹훅 등록/수정 (PUT /webhooks/config)

        Args:
            webhook_url: HTTPS 웹훅 수신 URL
            events: 구독할 이벤트 목록 (None이면 전체 구독)
            description: 설명

        Returns:
            등록 결과 (secretKey 포함 — 최초 등록 시에만 전체 값 반환)
        """
        data: dict[str, Any] = {"webhookUrl": webhook_url}
        if events is not None:
            data["events"] = events
        if description:
            data["description"] = description

        return await self._request("PUT", "/webhooks/config", json_data=data)

    async def get_webhook_config(self) -> dict[str, Any]:
        """웹훅 설정 조회 (GET /webhooks/config)"""
        return await self._request("GET", "/webhooks/config")

    async def delete_webhook(self) -> dict[str, Any]:
        """웹훅 비활성화 (DELETE /webhooks/config)"""
        return await self._request("DELETE", "/webhooks/config")

    async def send_test_webhook(self, event_type: str = "order.paid") -> dict[str, Any]:
        """테스트 웹훅 이벤트 전송 (POST /webhooks/test)"""
        return await self._request("POST", "/webhooks/test", json_data={
            "eventType": event_type,
        })

    async def get_webhook_deliveries(
        self,
        event_type: str | None = None,
        delivery_status: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """웹훅 전송 이력 조회 (GET /webhooks/deliveries)"""
        params: dict[str, Any] = {"limit": limit}
        if event_type:
            params["eventType"] = event_type
        if delivery_status:
            params["status"] = delivery_status

        return await self._request("GET", "/webhooks/deliveries", params=params)

    # === Full Workflow ===

    async def execute_order_workflow(
        self,
        title: str,
        book_spec_uid: str,
        pages_data: list[dict],
        cover_image_path: str | None,
        shipping: dict[str, str],
    ) -> dict[str, Any]:
        """전체 주문 워크플로우 실행

        1. 충전금 확인/충전
        2. 책 생성
        3. 사진 업로드
        4. 템플릿 조회
        5. 표지 생성
        6. 내지 삽입
        7. 최종화
        8. 견적 조회
        9. 주문 생성

        Args:
            title: 책 제목
            book_spec_uid: 판형 UID
            pages_data: [{"text": "...", "image_path": "..."}, ...]
            cover_image_path: 표지 이미지 경로 (None이면 첫 페이지 이미지 사용)
            shipping: 배송 정보
        Returns:
            주문 결과 dict
        """
        # 1. 충전금 확인/충전
        await self.ensure_sufficient_credits()

        # 2. 책 생성
        book_uid = await self.create_book(title, book_spec_uid)
        logger.info(f"Book Print 책 생성 완료: {book_uid}")

        # 3. 사진 업로드 — 페이지 이미지들
        uploaded_files: dict[str, str] = {}  # local_path -> remote_fileName
        all_image_paths = []

        if cover_image_path and os.path.exists(cover_image_path):
            all_image_paths.append(cover_image_path)

        for page in pages_data:
            img_path = page.get("image_path", "")
            if img_path and os.path.exists(img_path) and img_path not in uploaded_files:
                all_image_paths.append(img_path)

        for img_path in all_image_paths:
            if img_path not in uploaded_files:
                try:
                    file_name = await self.upload_photo(book_uid, img_path)
                    uploaded_files[img_path] = file_name
                    logger.info(f"사진 업로드 완료: {img_path} -> {file_name}")
                except BookPrintAPIError as e:
                    logger.warning(f"사진 업로드 실패 ({img_path}): {e.message}")
                    # 더미 이미지의 경우 placeholder 생성
                    uploaded_files[img_path] = f"placeholder_{os.path.basename(img_path)}"

        # 4. 템플릿 조회
        cover_templates = await self.get_templates(book_spec_uid, "cover")
        content_templates = await self.get_templates(book_spec_uid, "content")

        cover_template_uid = cover_templates[0]["templateUid"] if cover_templates else None
        content_template_uid = content_templates[0]["templateUid"] if content_templates else None

        if not cover_template_uid or not content_template_uid:
            raise BookPrintAPIError("사용 가능한 템플릿이 없습니다")

        # 5. 표지 생성
        cover_file = None
        if cover_image_path and cover_image_path in uploaded_files:
            cover_file = uploaded_files[cover_image_path]
        elif pages_data and pages_data[0].get("image_path") in uploaded_files:
            cover_file = uploaded_files[pages_data[0]["image_path"]]

        await self.create_cover(
            book_uid,
            cover_template_uid,
            {"title": title},
            cover_file,
        )
        logger.info("표지 생성 완료")

        # 6. 내지 삽입 (페이지별) — 실패 시 워크플로우 중단
        content_insert_failures = 0
        for i, page in enumerate(pages_data):
            text = page.get("text", "")
            img_path = page.get("image_path", "")
            img_file_name = uploaded_files.get(img_path, "")

            params: dict[str, Any] = {}
            if text:
                params["text"] = text
            if img_file_name:
                params["photo"] = img_file_name

            try:
                await self.insert_content(
                    book_uid,
                    content_template_uid,
                    params,
                    break_before="page",
                )
                logger.info(f"내지 삽입 완료: 페이지 {i + 1}")
            except BookPrintAPIError as e:
                content_insert_failures += 1
                logger.error(f"내지 삽입 실패 (페이지 {i + 1}): {e.message}")
                # 1개라도 실패하면 불완전한 책이므로 워크플로우 중단
                raise BookPrintAPIError(
                    f"내지 삽입 실패 (페이지 {i + 1}): {e.message}. 불완전한 책의 최종화를 방지하기 위해 워크플로우를 중단합니다.",
                    status_code=e.status_code,
                )

        # 7. 페이지 수 사전 검증 (판형별 범위 체크)
        total_pages = len(pages_data)
        spec_info = BOOK_SPEC_UIDS.get(book_spec_uid)
        if spec_info:
            page_min = spec_info["page_min"]
            page_max = spec_info["page_max"]
            if total_pages < page_min or total_pages > page_max:
                raise BookPrintAPIError(
                    f"페이지 수({total_pages})가 판형 제약을 벗어납니다 "
                    f"({book_spec_uid}: {page_min}~{page_max}페이지)",
                )

        # 8. 최종화
        finalize_result = await self.finalize_book(book_uid)
        logger.info(f"최종화 완료: {finalize_result}")

        # 9. 견적 조회
        estimate = await self.get_estimate(book_uid)
        logger.info(f"견적: {estimate}")

        # 충전금 부족 시 추가 충전
        if not estimate.get("creditSufficient", True):
            required = estimate.get("paidCreditAmount", 0)
            await self.sandbox_charge(max(required * 2, SANDBOX_CHARGE_AMOUNT))
            estimate = await self.get_estimate(book_uid)

        # 10. 주문 생성
        try:
            order_result = await self.create_order(book_uid, shipping)
        except BookPrintAPIError as e:
            if e.status_code == 402:
                # 충전금 부족 — 자동 충전 후 재시도
                logger.info("충전금 부족, 자동 충전 후 재시도")
                await self.sandbox_charge()
                order_result = await self.create_order(book_uid, shipping)
            else:
                raise

        logger.info(f"주문 생성 완료: {order_result.get('orderUid')}")

        return {
            "book_uid": book_uid,
            "order_uid": order_result.get("orderUid"),
            "order_status": order_result.get("orderStatus", 20),
            "order_status_display": order_result.get("orderStatusDisplay", "결제완료"),
            "total_amount": order_result.get("totalAmount", 0),
            "paid_credit_amount": order_result.get("paidCreditAmount", 0),
            "estimate": estimate,
            "order_data": order_result,
        }
