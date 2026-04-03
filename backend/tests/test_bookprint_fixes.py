"""통합 수정 검증 테스트 — INTEGRATION_REPORT.md 문제 수정 확인"""
import os
import tempfile
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.bookprint import (
    BookPrintService,
    BookPrintAPIError,
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


# === Fix #4: 템플릿 선택 로직 테스트 ===

class TestTemplateSelection:
    """_select_best_template 및 _select_best_content_template"""

    @pytest.mark.asyncio
    async def test_select_simplest_cover_template(self):
        """파라미터가 가장 적은 cover 템플릿 선택"""
        service = BookPrintService(api_key="test", base_url="http://test")

        templates = [
            {"templateUid": "tpl_complex"},
            {"templateUid": "tpl_simple"},
            {"templateUid": "tpl_medium"},
        ]

        async def mock_detail(uid):
            details = {
                "tpl_complex": {"parameters": {"a": {}, "b": {}, "c": {}, "d": {}}},
                "tpl_simple": {"parameters": {}},
                "tpl_medium": {"parameters": {"x": {}, "y": {}}},
            }
            return details.get(uid, {"parameters": {}})

        service.get_template_detail = mock_detail
        uid, params = await service._select_best_template(templates)

        assert uid == "tpl_simple"
        assert params == {}

    @pytest.mark.asyncio
    async def test_select_empty_content_template(self):
        """빈 내지 템플릿(파라미터 없음)을 우선 선택"""
        service = BookPrintService(api_key="test", base_url="http://test")

        templates = [
            {"templateUid": "tpl_diary"},
            {"templateUid": "tpl_empty"},
        ]

        async def mock_detail(uid):
            details = {
                "tpl_diary": {"parameters": {
                    "year": {"binding": "text"},
                    "month": {"binding": "text"},
                    "diaryText": {"binding": "text"},
                    "photo1": {"binding": "file"},
                }},
                "tpl_empty": {"parameters": {}},
            }
            return details.get(uid, {"parameters": {}})

        service.get_template_detail = mock_detail
        uid, params = await service._select_best_content_template(templates)

        assert uid == "tpl_empty"
        assert params == {}

    @pytest.mark.asyncio
    async def test_select_fallback_when_api_fails(self):
        """API 조회 실패 시 첫 번째 템플릿으로 폴백"""
        service = BookPrintService(api_key="test", base_url="http://test")

        templates = [{"templateUid": "tpl_fallback"}]

        async def mock_detail(uid):
            raise BookPrintAPIError("API 오류")

        service.get_template_detail = mock_detail
        uid, params = await service._select_best_content_template(templates)

        assert uid == "tpl_fallback"
        assert params == {}


# === Fix #2: 표지 파라미터 매핑 테스트 ===

class TestBuildCoverParameters:
    """_build_cover_parameters — 표지 필수 파라미터 동적 매핑"""

    def test_maps_all_required_cover_params(self):
        """frontPhoto, dateRange, spineTitle 등 필수 파라미터 모두 매핑"""
        params_def = {
            "frontPhoto": {"binding": "file", "type": "string"},
            "dateRange": {"binding": "text", "type": "string"},
            "spineTitle": {"binding": "text", "type": "string"},
        }

        result = BookPrintService._build_cover_parameters(
            title="테스트 동화책",
            params_def=params_def,
            cover_file_name="photo123.jpg",
        )

        assert result["frontPhoto"] == "photo123.jpg"
        assert result["spineTitle"] == "테스트 동화책"[:20]
        assert result["dateRange"]  # 날짜 문자열이 비어있지 않아야 함

    def test_empty_params_def_returns_empty(self):
        """빈 파라미터 정의 → 빈 dict"""
        result = BookPrintService._build_cover_parameters("제목", {}, "file.jpg")
        assert result == {}

    def test_title_param_maps_to_title(self):
        """title 파라미터에 책 제목 매핑"""
        params_def = {
            "bookTitle": {"binding": "text", "type": "string"},
        }
        result = BookPrintService._build_cover_parameters("내 동화책", params_def, None)
        assert result["bookTitle"] == "내 동화책"


# === Fix #1: 내지 파라미터 매핑 테스트 ===

class TestBuildContentParameters:
    """_build_content_parameters — 내지 템플릿 파라미터 동적 매핑"""

    def test_empty_template_returns_empty(self):
        """빈 템플릿(파라미터 없음) → 빈 dict"""
        result = BookPrintService._build_content_parameters({}, "텍스트", "img.jpg", 1)
        assert result == {}

    def test_diary_template_mapping(self):
        """diary 스타일 템플릿의 파라미터 매핑"""
        params_def = {
            "year": {"binding": "text", "type": "string"},
            "month": {"binding": "text", "type": "string"},
            "date": {"binding": "text", "type": "string"},
            "diaryText": {"binding": "text", "type": "string"},
            "photo1": {"binding": "file", "type": "string"},
        }
        result = BookPrintService._build_content_parameters(
            params_def, "오늘의 이야기", "uploaded_photo.jpg", 3
        )

        assert result["year"] == str(datetime.now().year)
        assert result["month"] == str(datetime.now().month)
        assert result["diaryText"] == "오늘의 이야기"
        assert result["photo1"] == "uploaded_photo.jpg"

    def test_simple_photo_label_template(self):
        """photo + dayLabel 템플릿 매핑"""
        params_def = {
            "photo": {"binding": "file", "type": "string"},
            "dayLabel": {"binding": "text", "type": "string"},
        }
        result = BookPrintService._build_content_parameters(
            params_def, "내용 텍스트", "img.jpg", 5
        )

        assert result["photo"] == "img.jpg"
        assert result["dayLabel"] == "Page 5"

    def test_gallery_binding_maps_to_array(self):
        """rowGallery 바인딩은 배열로 매핑"""
        params_def = {
            "photos": {"binding": "rowGallery", "type": "string"},
        }
        result = BookPrintService._build_content_parameters(
            params_def, "", "uploaded.jpg", 1
        )
        assert result["photos"] == ["uploaded.jpg"]

    def test_no_image_skips_file_param(self):
        """이미지가 없으면 file 파라미터 건너뜀"""
        params_def = {
            "photo1": {"binding": "file", "type": "string"},
            "diaryText": {"binding": "text", "type": "string"},
        }
        result = BookPrintService._build_content_parameters(
            params_def, "텍스트만", "", 1
        )
        assert "photo1" not in result
        assert result["diaryText"] == "텍스트만"


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
