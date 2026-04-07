"""Book Print API 연동 서비스

Sandbox 충전금 확인/충전, 책 생성, 사진 업로드, 표지/내지 생성,
최종화, 견적 조회, 주문 생성까지의 전체 워크플로우를 처리한다.

동화책 24페이지 구조:
  표지:       4Fy1mpIlm1ek (구글포토북C 표지)
  p1 (간지):  PorGJvT0oO7m (제목 페이지)
  p2~p23:    그림(5TLmcVySw3Ca) + 스토리(7AtlblwFXwPE) × 11
  p24:       5oRDpEfVerdC (발행면)
"""
import asyncio
import json
import httpx
import logging
import mimetypes
import os
from datetime import datetime
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

# 자동 충전 금액 (Sandbox)
SANDBOX_CHARGE_AMOUNT = 1_000_000

# ============================================================
# 동화책 템플릿 UID (하드코딩)
# 모든 템플릿은 SQUAREBOOK_HC 판형, public 또는 사용 가능 확인 완료
# ============================================================
TPL_COVER = "4SezofiW67xk"        # 커스텀 표지 (coverPhoto, subtitle, author)
TPL_TITLE_PAGE = "uZICIRIwJzuB"    # 커스텀 간지 → 제목 페이지 (monthYearTitle, author)
TPL_ILLUSTRATION = "5TLmcVySw3Ca"  # 커스텀 내지 — 그림 페이지 (photo)
TPL_STORY = "7AtlblwFXwPE"         # 커스텀 내지 — 스토리 페이지 (storyText)
TPL_PUBLISH = "5gBcekhFJVNT"       # 커스텀 발행면 (title, publishDate, author, ...)
TPL_BLANK = "2mi1ao0Z4Vxl"         # 공용 빈내지 (파라미터 없음)

# 판형 데이터 캐시 (서버 시작 시 API에서 로드)
BOOK_SPEC_CACHE: dict[str, dict] = {}


def get_book_specs() -> dict[str, dict]:
    """캐시된 판형 데이터 반환"""
    return BOOK_SPEC_CACHE


async def load_book_specs():
    """Book Print API에서 판형 목록을 조회하여 캐시에 저장"""
    global BOOK_SPEC_CACHE
    settings = get_settings()
    if not settings.BOOKPRINT_API_KEY:
        logger.warning("BOOKPRINT_API_KEY 미설정 — 판형 로드 스킵")
        return

    try:
        service = BookPrintService()
        result = await service._request("GET", "/book-specs")
        await service.close()

        specs = {}
        for item in result.get("data", []):
            uid = item.get("bookSpecUid", "")
            name = item.get("name", "")
            # 유효한 데이터만 캐시 (이름, 크기가 있는 것)
            if name and item.get("innerTrimWidthMm", 0) > 0:
                specs[uid] = {
                    "name": name,
                    "width_mm": item["innerTrimWidthMm"],
                    "height_mm": item["innerTrimHeightMm"],
                    "page_min": item.get("pageMin", 24),
                    "page_max": item.get("pageMax", 130),
                    "cover_type": item.get("coverType", ""),
                    "binding_type": item.get("bindingType", ""),
                }

        if specs:
            BOOK_SPEC_CACHE = specs
            logger.info(f"[bookprint] 판형 {len(specs)}개 로드: {list(specs.keys())}")
        else:
            logger.warning("[bookprint] 유효한 판형이 없습니다")
    except Exception as e:
        logger.error(f"[bookprint] 판형 로드 실패: {e}")


def detect_mime_type(file_path: str) -> str:
    """파일의 MIME type을 확장자 및 magic bytes로 감지한다.

    Book Print API는 JPEG, PNG, WebP 등을 지원하므로,
    실제 파일 형식에 맞는 Content-Type을 전송해야 한다.
    """
    # 1) magic bytes 기반 감지 (가장 정확)
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        if header[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        if header[:2] == b'\xff\xd8':
            return "image/jpeg"
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return "image/webp"
        if header[:3] == b'GIF':
            return "image/gif"
        if header[:2] in (b'BM',):
            return "image/bmp"
    except (IOError, OSError):
        pass

    # 2) 확장자 기반 폴백
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith("image/"):
        return mime

    # 3) 기본값
    return "image/png"


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

        content_type = detect_mime_type(file_path)
        with open(file_path, "rb") as f:
            files = [("file", (os.path.basename(file_path), f, content_type))]
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

    async def get_template_detail(self, template_uid: str) -> dict:
        """템플릿 상세 조회 — 파라미터 정의 포함

        API 응답 구조: data.parameters.definitions = {paramName: {binding, required, ...}}
        호출자 편의를 위해 parameters.definitions를 parameters로 끌어올린다.
        """
        result = await self._request("GET", f"/templates/{template_uid}")
        data = result.get("data", {})
        # parameters.definitions 언래핑: API 문서 기준 실제 파라미터 정의는
        # data.parameters.definitions 안에 중첩되어 있음
        params = data.get("parameters", {})
        if isinstance(params, dict) and "definitions" in params:
            data["parameters"] = params["definitions"]
        return data

    # === Covers API ===

    async def create_cover(self, book_uid: str, template_uid: str, parameters: dict) -> dict:
        """표지 생성"""
        form_data: dict[str, Any] = {
            "templateUid": template_uid,
            "parameters": json.dumps(parameters),
        }

        # API는 multipart/form-data를 기대 — files 형식으로 전달
        multipart_fields = {k: (None, v) for k, v in form_data.items()}
        result = await self._request("POST", f"/books/{book_uid}/cover", files=multipart_fields)
        return result.get("data", {})

    # === Contents API ===

    async def insert_content(self, book_uid: str, template_uid: str, parameters: dict, break_before: str = "page") -> dict:
        """내지 삽입

        Returns:
            API 응답 data + cursor 정보 (pageNum, pageSide).
            pageSide는 삽입된 콘텐츠가 left/right 중 어디에 배치됐는지 나타냄.
        """
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
        data = result.get("data", {})

        # cursor 정보 병합 (pageNum, pageSide)
        cursor = result.get("cursor", {})
        if cursor:
            data["pageNum"] = cursor.get("pageNum")
            data["pageSide"] = cursor.get("pageSide")

        return data

    # === Finalization ===

    async def finalize_book(self, book_uid: str) -> dict:
        """책 최종화"""
        result = await self._request("POST", f"/books/{book_uid}/finalization", json_data={})
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

    # === Render / Thumbnails ===

    async def download_thumbnails(self, book_uid: str, out_dir: str) -> dict[str, Any]:
        """Book Print API 렌더링 썸네일을 다운로드하여 파일로 저장한다.

        Args:
            book_uid: Book Print API의 bookUid
            out_dir: 저장 디렉토리 경로

        Returns:
            {"cover": "path/to/cover.jpg", "pages": ["path/to/0.jpg", ...]}
        """
        os.makedirs(out_dir, exist_ok=True)
        client = await self._get_client()
        headers = self._headers()

        # 1. 전 페이지 렌더 요청 (24페이지)
        for pn in range(24):
            try:
                await self._request("POST", "/render/page-thumbnail", json_data={
                    "bookUid": book_uid,
                    "pageNum": pn,
                })
            except BookPrintAPIError as e:
                logger.warning(f"[bookprint] 렌더 요청 실패 (page {pn}): {e.message}")

        # 2. 렌더링 완료 대기
        await asyncio.sleep(5)

        result: dict[str, Any] = {"cover": None, "pages": []}

        # 3. 표지 다운로드
        cover_path = os.path.join(out_dir, "cover.jpg")
        for attempt in range(2):
            try:
                r = await client.get(
                    f"{self.base_url}/render/thumbnail/{book_uid}/cover.jpg",
                    headers=headers, timeout=30.0,
                )
                if r.status_code == 200:
                    with open(cover_path, "wb") as f:
                        f.write(r.content)
                    result["cover"] = cover_path
                    break
                elif r.status_code == 404 and attempt == 0:
                    await asyncio.sleep(3)
            except Exception as e:
                logger.warning(f"[bookprint] 표지 썸네일 다운로드 실패: {e}")

        # 4. 내지 다운로드 (0~23)
        for pn in range(24):
            page_path = os.path.join(out_dir, f"{pn}.jpg")
            for attempt in range(2):
                try:
                    r = await client.get(
                        f"{self.base_url}/render/thumbnail/{book_uid}/{pn}.jpg",
                        headers=headers, timeout=30.0,
                    )
                    if r.status_code == 200:
                        with open(page_path, "wb") as f:
                            f.write(r.content)
                        result["pages"].append(page_path)
                        break
                    elif r.status_code == 404 and attempt == 0:
                        await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"[bookprint] 썸네일 다운로드 실패 (page {pn}): {e}")

        logger.info(f"[bookprint] 썸네일 다운로드 완료: cover={'O' if result['cover'] else 'X'}, pages={len(result['pages'])}/24")
        return result

    # === Full Workflow ===

    async def execute_order_workflow(
        self,
        title: str,
        book_spec_uid: str,
        pages_data: list[dict],
        cover_image_path: str | None,
        shipping: dict[str, str],
        child_name: str = "",
    ) -> dict[str, Any]:
        """전체 주문 워크플로우 실행

        동화책 24페이지 구조:
          표지:      TPL_COVER (coverPhoto, subtitle, dateRange)
          p1 (간지): TPL_TITLE_PAGE (monthYearTitle, recordTitle)
          p2~p23:   TPL_ILLUSTRATION(photo) + TPL_STORY(storyText) × 11
          p24:      TPL_PUBLISH (title, publishDate, author, ...)

        Args:
            title: 책 제목
            book_spec_uid: 판형 UID
            pages_data: [{"text": "...", "image_path": "...", "page_type": "..."}, ...]
            cover_image_path: 표지 이미지 경로 (None이면 첫 일러스트 사용)
            shipping: 배송 정보
            child_name: 아이 이름 (발행면 저자)
        Returns:
            주문 결과 dict
        """
        # 1. 충전금 확인/충전
        await self.ensure_sufficient_credits()

        # 2. 책 생성
        book_uid = await self.create_book(title, book_spec_uid)
        logger.info(f"[bookprint] 책 생성 완료: {book_uid}")

        # 3. 사진 업로드 — illustration 타입 페이지의 이미지만
        uploaded_files: dict[str, str] = {}  # local_path -> remote_fileName

        # 표지 이미지
        if cover_image_path and os.path.exists(cover_image_path):
            try:
                file_name = await self.upload_photo(book_uid, cover_image_path)
                uploaded_files[cover_image_path] = file_name
                logger.info(f"[bookprint] 표지 사진 업로드: {file_name}")
            except BookPrintAPIError as e:
                logger.warning(f"[bookprint] 표지 사진 업로드 실패: {e.message}")

        # 페이지 이미지 (illustration 타입만)
        for page in pages_data:
            if page.get("page_type") != "illustration":
                continue
            img_path = page.get("image_path", "")
            if img_path and os.path.exists(img_path) and img_path not in uploaded_files:
                try:
                    file_name = await self.upload_photo(book_uid, img_path)
                    uploaded_files[img_path] = file_name
                    logger.info(f"[bookprint] 사진 업로드: p{page['page_number']} -> {file_name}")
                except BookPrintAPIError as e:
                    logger.warning(f"[bookprint] 사진 업로드 실패 (p{page['page_number']}): {e.message}")

        # 4. 표지 생성
        cover_file = uploaded_files.get(cover_image_path, "")
        if not cover_file:
            # 표지 이미지 없으면 첫 일러스트 사용
            for page in pages_data:
                if page.get("page_type") == "illustration":
                    cover_file = uploaded_files.get(page.get("image_path", ""), "")
                    if cover_file:
                        break

        cover_params = {
            "subtitle": title,
            "author": child_name or "",
        }
        if cover_file:
            cover_params["coverPhoto"] = cover_file
        else:
            logger.warning("[bookprint] 표지 이미지 없음 — coverPhoto 파라미터 생략")
        await self.create_cover(book_uid, TPL_COVER, cover_params)
        logger.info("[bookprint] 표지 생성 완료")

        # 5. 페이지별 내지 삽입
        #    colophon(발행면)은 따로 처리 — pageSide 체크 후 삽입
        inserted_count = 0
        last_result: dict = {}
        content_pages = [p for p in pages_data if p.get("page_type") != "colophon"]
        colophon_page = next((p for p in pages_data if p.get("page_type") == "colophon"), None)

        for page in content_pages:
            page_type = page.get("page_type", "")
            page_num = page.get("page_number", 0)
            text = page.get("text", "")
            img_path = page.get("image_path", "")

            try:
                if page_type == "title":
                    # p1: 간지 (제목 페이지, templateKind=divider)
                    last_result = await self.insert_content(book_uid, TPL_TITLE_PAGE, {
                        "monthYearTitle": title,
                        "author": child_name or "",
                    }, break_before="page")

                elif page_type == "illustration":
                    # 그림 페이지 (왼쪽)
                    img_file = uploaded_files.get(img_path, "")
                    if img_file:
                        last_result = await self.insert_content(book_uid, TPL_ILLUSTRATION, {"photo": img_file}, break_before="page")
                    else:
                        # 이미지 없으면 빈내지로 대체 (photo 필수 파라미터 누락 방지)
                        logger.warning(f"[bookprint] 그림 이미지 없음 (p{page_num}) — 빈내지로 대체")
                        last_result = await self.insert_content(book_uid, TPL_BLANK, {}, break_before="page")

                elif page_type == "story":
                    # 스토리 페이지 (오른쪽)
                    last_result = await self.insert_content(book_uid, TPL_STORY, {
                        "storyText": text,
                    }, break_before="page")

                else:
                    # 알 수 없는 타입 → 빈내지
                    last_result = await self.insert_content(book_uid, TPL_BLANK, {}, break_before="page")

                inserted_count += 1
                page_side = last_result.get("pageSide", "?")
                logger.info(f"[bookprint] 내지 삽입 완료: p{page_num} ({page_type}) → pageSide={page_side}")

            except BookPrintAPIError as e:
                logger.error(f"[bookprint] 내지 삽입 실패 (p{page_num} {page_type}): {e.message}")
                raise BookPrintAPIError(
                    f"내지 삽입 실패 (p{page_num} {page_type}): {e.message}",
                    status_code=e.status_code,
                )

        # 5b. 발행면 삽입 — pageSide 체크 후 위치 보장
        #     발행면(templateKind=publish)은 left에 와야 함.
        #     마지막 내지가 left에 있으면 빈내지를 끼워서 발행면이 left에 오게 함.
        if colophon_page:
            last_side = last_result.get("pageSide", "right")
            if last_side == "left":
                logger.info("[bookprint] 발행면 위치 조정: 빈내지 삽입 (마지막 내지가 left)")
                last_result = await self.insert_content(book_uid, TPL_BLANK, {}, break_before="page")
                inserted_count += 1

            now = datetime.now()
            last_result = await self.insert_content(book_uid, TPL_PUBLISH, {
                "title": title,
                "publishDate": now.strftime("%Y년 %m월 %d일"),
                "author": child_name or "AI 동화작가",
                "hashtags": "#AI동화 #꿈꾸는나 #스위트북",
                "publisher": "(주)스위트북",
            }, break_before="page")
            inserted_count += 1
            logger.info(f"[bookprint] 발행면 삽입 완료: pageSide={last_result.get('pageSide', '?')}")

        # 5c. 삽입 검증 — 예상 페이지 수와 실제 삽입 수 비교
        expected_count = len(pages_data)
        if inserted_count < expected_count:
            logger.warning(
                f"[bookprint] 페이지 삽입 불일치: 예상 {expected_count}개, 실제 {inserted_count}개"
            )

        # 6. 최종화
        finalize_result = await self.finalize_book(book_uid)
        logger.info(f"[bookprint] 최종화 완료: {finalize_result}")

        # 7. 견적 조회
        estimate = await self.get_estimate(book_uid)
        logger.info(f"[bookprint] 견적: {estimate}")

        # 충전금 부족 시 추가 충전
        if not estimate.get("creditSufficient", True):
            required = estimate.get("paidCreditAmount", 0)
            await self.sandbox_charge(max(required * 2, SANDBOX_CHARGE_AMOUNT))
            estimate = await self.get_estimate(book_uid)

        # 8. 주문 생성
        try:
            order_result = await self.create_order(book_uid, shipping)
        except BookPrintAPIError as e:
            if e.status_code == 402:
                logger.info("[bookprint] 충전금 부족, 자동 충전 후 재시도")
                await self.sandbox_charge()
                order_result = await self.create_order(book_uid, shipping)
            else:
                raise

        logger.info(f"[bookprint] 주문 생성 완료: {order_result.get('orderUid')}")

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
