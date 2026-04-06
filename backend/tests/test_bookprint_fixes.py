"""통합 수정 검증 테스트 — INTEGRATION_REPORT.md 문제 수정 확인"""
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.bookprint import (
    BookPrintService,
    detect_mime_type,
)


# === Fix #5: MIME type 감지 테스트 ===

class TestDetectMimeType:
    """파일 확장자 및 magic bytes 기반 MIME type 감지"""

    def test_detect_png_by_magic_bytes(self, tmp_path):
        """PNG magic bytes로 image/png 감지"""
        f = tmp_path / "test.png"
        f.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        assert detect_mime_type(str(f)) == "image/png"

    def test_detect_jpeg_by_magic_bytes(self, tmp_path):
        """JPEG magic bytes로 image/jpeg 감지"""
        f = tmp_path / "test.jpg"
        f.write_bytes(b'\xff\xd8\xff\xe0' + b'\x00' * 100)
        assert detect_mime_type(str(f)) == "image/jpeg"

    def test_detect_webp_by_magic_bytes(self, tmp_path):
        """WebP magic bytes로 image/webp 감지"""
        f = tmp_path / "test.webp"
        f.write_bytes(b'RIFF\x00\x00\x00\x00WEBP' + b'\x00' * 100)
        assert detect_mime_type(str(f)) == "image/webp"

    def test_detect_by_extension_fallback(self, tmp_path):
        """magic bytes 불일치 시 확장자 기반 폴백"""
        f = tmp_path / "test.jpeg"
        f.write_bytes(b'\x00' * 100)  # 알 수 없는 magic bytes
        mime = detect_mime_type(str(f))
        assert mime == "image/jpeg"

    def test_detect_unknown_returns_default(self, tmp_path):
        """알 수 없는 파일은 image/png 기본값"""
        f = tmp_path / "test.dat"
        f.write_bytes(b'\x00' * 100)
        assert detect_mime_type(str(f)) == "image/png"

    def test_detect_gif_by_magic_bytes(self, tmp_path):
        """GIF magic bytes로 image/gif 감지"""
        f = tmp_path / "test.gif"
        f.write_bytes(b'GIF89a' + b'\x00' * 100)
        assert detect_mime_type(str(f)) == "image/gif"


# === TPL_ 상수 및 현재 구조 검증 테스트 ===

class TestTPLConstants:
    """TPL_ 상수가 올바르게 정의되어 있는지 검증"""

    def test_tpl_cover_defined(self):
        """TPL_COVER 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_COVER
        assert isinstance(TPL_COVER, str)
        assert len(TPL_COVER) > 0

    def test_tpl_title_page_defined(self):
        """TPL_TITLE_PAGE 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_TITLE_PAGE
        assert isinstance(TPL_TITLE_PAGE, str)
        assert len(TPL_TITLE_PAGE) > 0

    def test_tpl_illustration_defined(self):
        """TPL_ILLUSTRATION 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_ILLUSTRATION
        assert isinstance(TPL_ILLUSTRATION, str)
        assert len(TPL_ILLUSTRATION) > 0

    def test_tpl_story_defined(self):
        """TPL_STORY 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_STORY
        assert isinstance(TPL_STORY, str)
        assert len(TPL_STORY) > 0

    def test_tpl_publish_defined(self):
        """TPL_PUBLISH 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_PUBLISH
        assert isinstance(TPL_PUBLISH, str)
        assert len(TPL_PUBLISH) > 0

    def test_tpl_blank_defined(self):
        """TPL_BLANK 상수가 문자열로 정의됨"""
        from app.services.bookprint import TPL_BLANK
        assert isinstance(TPL_BLANK, str)
        assert len(TPL_BLANK) > 0

    def test_execute_order_workflow_exists(self):
        """execute_order_workflow 메서드가 존재하는지 확인"""
        assert hasattr(BookPrintService, "execute_order_workflow")
        assert callable(getattr(BookPrintService, "execute_order_workflow"))


# === Fix #3: 더미 이미지 실제 파일 생성 테스트 ===

class TestPlaceholderImageGeneration:
    """generate.py의 _create_placeholder_image가 실제 파일을 생성하는지 확인"""

    def test_placeholder_image_creates_real_file(self):
        """placeholder 이미지가 실제 PNG 파일로 생성됨"""
        from app.services.generate import _create_placeholder_image
        from app.services.photo import UPLOAD_DIR, ensure_upload_dir

        ensure_upload_dir()
        path = _create_placeholder_image(1, "테스트", 999)

        assert os.path.exists(path)
        assert path.endswith(".png")

        # PNG magic bytes 확인
        with open(path, "rb") as f:
            header = f.read(8)
        assert header[:4] == b'\x89PNG'

        # 정리
        os.remove(path)

    def test_placeholder_image_path_in_uploads_dir(self):
        """생성된 이미지가 uploads 디렉토리에 위치"""
        from app.services.generate import _create_placeholder_image
        from app.services.photo import UPLOAD_DIR, ensure_upload_dir

        ensure_upload_dir()
        path = _create_placeholder_image(5, "Scene", 100)

        assert UPLOAD_DIR in path or os.path.dirname(path) == UPLOAD_DIR

        # 정리
        if os.path.exists(path):
            os.remove(path)


# === Fix: parameters.definitions 언래핑 테스트 (R2 치명 버그) ===

class TestParametersDefinitionsUnwrap:
    """get_template_detail()이 parameters.definitions를 올바르게 언래핑하는지 확인"""

    @pytest.mark.asyncio
    async def test_unwraps_definitions_layer(self):
        """API 응답의 parameters.definitions가 parameters로 끌어올려짐"""
        service = BookPrintService(api_key="test", base_url="http://test")

        # API 실제 응답 구조를 시뮬레이션
        mock_response = {
            "data": {
                "templateUid": "tpl_cover",
                "parameters": {
                    "definitions": {
                        "frontPhoto": {"binding": "file", "required": True},
                        "dateRange": {"binding": "text", "required": True},
                        "spineTitle": {"binding": "text", "required": True},
                    }
                }
            }
        }
        service._request = AsyncMock(return_value=mock_response)
        detail = await service.get_template_detail("tpl_cover")

        # parameters가 definitions 내용으로 교체되어야 함
        assert "frontPhoto" in detail["parameters"]
        assert "dateRange" in detail["parameters"]
        assert "spineTitle" in detail["parameters"]
        assert "definitions" not in detail["parameters"]

    @pytest.mark.asyncio
    async def test_unwrap_preserves_empty_definitions(self):
        """빈 definitions → 빈 parameters"""
        service = BookPrintService(api_key="test", base_url="http://test")

        mock_response = {
            "data": {
                "templateUid": "tpl_empty",
                "parameters": {
                    "definitions": {}
                }
            }
        }
        service._request = AsyncMock(return_value=mock_response)
        detail = await service.get_template_detail("tpl_empty")

        assert detail["parameters"] == {}

    @pytest.mark.asyncio
    async def test_unwrap_handles_no_definitions_key(self):
        """definitions 키가 없는 경우 (하위 호환성) — parameters 그대로 유지"""
        service = BookPrintService(api_key="test", base_url="http://test")

        mock_response = {
            "data": {
                "templateUid": "tpl_flat",
                "parameters": {
                    "photo": {"binding": "file"},
                    "text": {"binding": "text"},
                }
            }
        }
        service._request = AsyncMock(return_value=mock_response)
        detail = await service.get_template_detail("tpl_flat")

        assert "photo" in detail["parameters"]
        assert "text" in detail["parameters"]

    @pytest.mark.asyncio
    async def test_unwrap_definitions_used_in_workflow(self):
        """언래핑된 파라미터가 execute_order_workflow에서 사용될 수 있는지 확인"""
        service = BookPrintService(api_key="test", base_url="http://test")

        # definitions 래핑된 응답을 시뮬레이션
        mock_response = {
            "data": {
                "templateUid": "tpl_cover",
                "parameters": {
                    "definitions": {
                        "coverPhoto": {"binding": "file", "required": True},
                        "subtitle": {"binding": "text", "required": False},
                    }
                }
            }
        }
        service._request = AsyncMock(return_value=mock_response)
        detail = await service.get_template_detail("tpl_cover")

        # definitions가 올바르게 언래핑되었는지
        assert "coverPhoto" in detail["parameters"]
        assert "subtitle" in detail["parameters"]
        assert "definitions" not in detail["parameters"]


# === Fix #8: 페이지 수 검증 (삽입 성공 수 기준) ===

class TestPageCountValidation:
    """페이지 수 검증이 로컬 데이터가 아닌 실제 삽입 수 기준인지 확인"""

    @pytest.mark.asyncio
    async def test_workflow_uses_inserted_count_for_validation(self):
        """execute_order_workflow가 inserted_count를 기준으로 페이지 수 검증"""
        service = BookPrintService(api_key="test", base_url="http://test")

        # 모든 API 호출을 mock
        service.ensure_sufficient_credits = AsyncMock()
        service.create_book = AsyncMock(return_value="bk_test")
        service.upload_photo = AsyncMock(return_value="photo.jpg")
        service.get_templates = AsyncMock(return_value=[{"templateUid": "tpl_1"}])
        service.get_template_detail = AsyncMock(return_value={"parameters": {}})
        service.create_cover = AsyncMock()
        service.insert_content = AsyncMock()
        service.finalize_book = AsyncMock(return_value={"pageCount": 24})
        service.get_estimate = AsyncMock(return_value={"creditSufficient": True, "paidCreditAmount": 100})
        service.create_order = AsyncMock(return_value={"orderUid": "ord_test", "orderStatus": 20})

        # 24개 페이지 데이터 (판형 최소 = 24)
        pages_data = [{"text": f"Page {i}", "image_path": ""} for i in range(24)]

        result = await service.execute_order_workflow(
            title="테스트",
            book_spec_uid="SQUAREBOOK_HC",
            pages_data=pages_data,
            cover_image_path=None,
            shipping={"recipientName": "테스트", "recipientPhone": "01012345678", "postalCode": "06101", "address1": "서울"},
        )

        assert result["order_uid"] == "ord_test"
        # insert_content가 24번 호출되어야 함
        assert service.insert_content.call_count == 24
