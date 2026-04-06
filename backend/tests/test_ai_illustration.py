"""태스크 17: AI 페이지 일러스트 생성 테스트 (GPT Image)

모든 테스트에서 OpenAI API를 mock 처리한다.
"""
import base64
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open

# ──────────────────────────────────────────────
# 유닛 테스트: ai_illustration 서비스
# ──────────────────────────────────────────────

class TestBuildIllustrationPrompt:
    """일러스트 프롬프트 구성 테스트"""

    def test_prompt_includes_art_style_keywords(self):
        from app.services.ai_illustration import _build_illustration_prompt
        prompt = _build_illustration_prompt(
            art_style="watercolor",
            scene_description="A child standing in front of a fire truck",
            child_name="민준",
            job_name="소방관",
        )
        assert "watercolor illustration" in prompt
        assert "soft warm tones" in prompt

    def test_prompt_includes_scene_description(self):
        from app.services.ai_illustration import _build_illustration_prompt
        prompt = _build_illustration_prompt(
            art_style="pencil",
            scene_description="A child holding a stethoscope in a hospital",
            child_name="서연",
            job_name="의사",
        )
        assert "A child holding a stethoscope in a hospital" in prompt

    def test_prompt_includes_job_outfit(self):
        from app.services.ai_illustration import _build_illustration_prompt
        prompt = _build_illustration_prompt(
            art_style="3d",
            scene_description="A child in a lab",
            child_name="민준",
            job_name="과학자",
        )
        assert "scientist" in prompt.lower() or "lab coat" in prompt.lower()

    def test_prompt_fallback_for_unknown_art_style(self):
        from app.services.ai_illustration import _build_illustration_prompt
        prompt = _build_illustration_prompt(
            art_style="unknown_style",
            scene_description="A scene",
            child_name="아이",
            job_name="직업",
        )
        # 알 수 없는 스타일이라도 프롬프트가 생성되어야 함
        assert "A scene" in prompt
        assert len(prompt) > 20


class TestGenerateIllustrationImage:
    """GPT Image API 호출 테스트 (mock)"""

    @patch("app.services.ai_illustration.get_settings")
    @patch("app.services.ai_illustration.OpenAI")
    def test_successful_generation(self, mock_openai_cls, mock_settings):
        """정상적인 일러스트 생성"""
        from app.services.ai_illustration import generate_illustration_image

        mock_settings.return_value.OPENAI_API_KEY = "test-key"
        fake_b64 = base64.b64encode(b"fake-png-data").decode()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json=fake_b64)]
        mock_client = MagicMock()
        mock_client.images.edit.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        with patch("builtins.open", mock_open(read_data=b"fake-image")):
            result = generate_illustration_image(
                character_sheet_path="/tmp/test_char.png",
                scene_description="A child at a fire station",
                art_style="watercolor",
                child_name="민준",
                job_name="소방관",
            )

        assert result == b"fake-png-data"
        mock_client.images.edit.assert_called_once()
        call_kwargs = mock_client.images.edit.call_args
        assert call_kwargs.kwargs["model"] == "gpt-image-1"
        assert call_kwargs.kwargs["size"] == "1024x1024"
        assert call_kwargs.kwargs["quality"] == "medium"

    @patch("app.services.ai_illustration.get_settings")
    @patch("app.services.ai_illustration.OpenAI")
    def test_content_policy_error(self, mock_openai_cls, mock_settings):
        """콘텐츠 정책 위반 시 적절한 에러"""
        from app.services.ai_illustration import (
            generate_illustration_image,
            IllustrationGenerationError,
        )
        from openai import BadRequestError

        mock_settings.return_value.OPENAI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_client.images.edit.side_effect = BadRequestError(
            message="content_policy_violation",
            response=MagicMock(status_code=400),
            body={"error": {"message": "content_policy_violation"}},
        )
        mock_openai_cls.return_value = mock_client

        with patch("builtins.open", mock_open(read_data=b"fake-image")):
            with pytest.raises(IllustrationGenerationError, match="콘텐츠 정책"):
                generate_illustration_image(
                    character_sheet_path="/tmp/test_char.png",
                    scene_description="scene",
                    art_style="watercolor",
                    child_name="민준",
                    job_name="소방관",
                )

    @patch("app.services.ai_illustration.get_settings")
    @patch("app.services.ai_illustration.OpenAI")
    def test_general_api_error(self, mock_openai_cls, mock_settings):
        """일반 API 오류 시 에러"""
        from app.services.ai_illustration import (
            generate_illustration_image,
            IllustrationGenerationError,
        )

        mock_settings.return_value.OPENAI_API_KEY = "test-key"
        mock_client = MagicMock()
        mock_client.images.edit.side_effect = Exception("network error")
        mock_openai_cls.return_value = mock_client

        with patch("builtins.open", mock_open(read_data=b"fake-image")):
            with pytest.raises(IllustrationGenerationError):
                generate_illustration_image(
                    character_sheet_path="/tmp/test_char.png",
                    scene_description="scene",
                    art_style="watercolor",
                    child_name="민준",
                    job_name="소방관",
                )


class TestGenerateIllustrationOrDummy:
    """AI 또는 더미 일러스트 생성 폴백 테스트"""

    @patch("app.services.ai_illustration.get_settings")
    def test_no_api_key_returns_none(self, mock_settings):
        """OPENAI_API_KEY 미설정 시 None 반환 (더미 폴백 트리거)"""
        from app.services.ai_illustration import generate_illustration_or_dummy

        mock_settings.return_value.OPENAI_API_KEY = ""

        result = generate_illustration_or_dummy(
            character_sheet_path="/tmp/test.png",
            scene_description="scene",
            art_style="watercolor",
            child_name="민준",
            job_name="소방관",
        )
        assert result is None

    @patch("app.services.ai_illustration.generate_illustration_image")
    @patch("app.services.ai_illustration.get_settings")
    def test_api_error_returns_none(self, mock_settings, mock_generate):
        """API 호출 실패 시 None 반환 (더미 폴백)"""
        from app.services.ai_illustration import (
            generate_illustration_or_dummy,
            IllustrationGenerationError,
        )

        mock_settings.return_value.OPENAI_API_KEY = "test-key"
        mock_generate.side_effect = IllustrationGenerationError("fail")

        result = generate_illustration_or_dummy(
            character_sheet_path="/tmp/test.png",
            scene_description="scene",
            art_style="watercolor",
            child_name="민준",
            job_name="소방관",
        )
        assert result is None

    @patch("app.services.ai_illustration.generate_illustration_image")
    @patch("app.services.ai_illustration.get_settings")
    def test_success_returns_bytes(self, mock_settings, mock_generate):
        """성공 시 이미지 바이트 반환"""
        from app.services.ai_illustration import generate_illustration_or_dummy

        mock_settings.return_value.OPENAI_API_KEY = "test-key"
        mock_generate.return_value = b"png-data"

        result = generate_illustration_or_dummy(
            character_sheet_path="/tmp/test.png",
            scene_description="scene",
            art_style="watercolor",
            child_name="민준",
            job_name="소방관",
        )
        assert result == b"png-data"


# ──────────────────────────────────────────────
# 통합 테스트: generate 서비스의 AI 일러스트 연동
# ──────────────────────────────────────────────

class TestGenerateStoryWithAIIllustration:
    """generate_story에서 AI 일러스트 생성 연동 테스트"""

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_ai_illustration_called_per_page(self, mock_illust, mock_story, client):
        """AI 일러스트가 페이지마다 호출되는지 확인"""
        mock_illust.return_value = None  # 더미 폴백
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        # AI 일러스트 생성은 페이지 수만큼 호출됨 (24페이지)
        assert mock_illust.call_count == 24

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_ai_illustration_success_saves_real_image(self, mock_illust, mock_story, client, tmp_path):
        """AI 일러스트 성공 시 실제 이미지가 저장되는지 확인"""
        # 간단한 PNG 바이트 (1x1 pixel)
        from PIL import Image
        import io
        img = Image.new("RGB", (10, 10), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        fake_png = buf.getvalue()

        mock_illust.return_value = fake_png
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        # 각 페이지에 이미지가 있어야 함
        for page in data["pages"]:
            assert len(page["images"]) >= 1
            # 이미지 경로에 ai_illust가 포함되어야 함
            assert "ai_illust" in page["images"][0]["image_path"]

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_ai_illustration_failure_falls_back_to_placeholder(self, mock_illust, mock_story, client):
        """AI 일러스트 실패 시 placeholder 이미지로 폴백"""
        mock_illust.return_value = None  # 실패 시 None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        # placeholder가 생성되어야 함
        for page in data["pages"]:
            assert len(page["images"]) >= 1


# ──────────────────────────────────────────────
# 통합 테스트: regenerate-image AI 호출
# ──────────────────────────────────────────────

class TestRegenerateImageAI:
    """regenerate-image 엔드포인트의 AI 호출 테스트"""

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    @patch("app.api.books.generate_illustration_or_dummy")
    def test_regenerate_calls_ai(self, mock_api_illust, mock_gen_illust, mock_story, client):
        """재생성 시 AI 일러스트가 호출되는지 확인"""
        mock_gen_illust.return_value = None
        mock_api_illust.return_value = None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        gen_res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert gen_res.status_code == 200
        page_id = gen_res.json()["pages"][0]["id"]

        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert mock_api_illust.called

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    @patch("app.api.books.generate_illustration_or_dummy")
    def test_regenerate_count_increments(self, mock_api_illust, mock_gen_illust, mock_story, client):
        """재생성 횟수가 정확히 증가하는지 확인"""
        mock_gen_illust.return_value = None
        mock_api_illust.return_value = None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        gen_res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        page_id = gen_res.json()["pages"][0]["id"]

        for i in range(4):
            res = client.post(
                f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
                headers=_auth_header(token),
            )
            assert res.status_code == 200
            assert res.json()["image_regen_count"] == i + 1

        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    @patch("app.api.books.generate_illustration_or_dummy")
    def test_regenerate_gallery_mode(self, mock_api_illust, mock_gen_illust, mock_story, client):
        """재생성 시 갤러리 방식 — 기존 이미지 유지 + 새 이미지 추가"""
        mock_gen_illust.return_value = None
        mock_api_illust.return_value = None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        gen_res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        page_id = gen_res.json()["pages"][0]["id"]

        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        images = res.json()["images"]
        assert len(images) == 2

        selected = [img for img in images if img["is_selected"]]
        assert len(selected) == 1
        assert selected[0]["generation_index"] == 1


# ──────────────────────────────────────────────
# 통합 테스트: 스토리 재생성 연쇄 처리
# ──────────────────────────────────────────────

class TestRegenerateStoryCascade:
    """스토리 재생성 시 이미지 폐기 + 새 일러스트 + 횟수 리셋"""

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_story_regen_resets_image_regen_count(self, mock_illust, mock_story, client):
        """스토리 재생성 시 이미지 재생성 횟수가 리셋되는지 확인"""
        mock_illust.return_value = None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        # 생성
        gen_res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        page_id = gen_res.json()["pages"][0]["id"]

        # 이미지 재생성 2회 수행 (image_regen_count = 2)
        with patch("app.api.books.generate_illustration_or_dummy", return_value=None):
            for _ in range(2):
                client.post(
                    f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
                    headers=_auth_header(token),
                )

        # 스토리 재생성
        regen_res = client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token),
        )
        assert regen_res.status_code == 200

        # 새 페이지의 image_regen_count 는 0이어야 함
        pages_res = client.get(
            f"/api/books/{book_id}/pages",
            headers=_auth_header(token),
        )
        for page in pages_res.json():
            assert page["image_regen_count"] == 0

    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_story_regen_creates_new_illustrations(self, mock_illust, client):
        """스토리 재생성 시 새 일러스트가 생성되는지 확인"""
        mock_illust.return_value = None

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        # 생성
        client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )

        # 호출 횟수 리셋
        mock_illust.reset_mock()

        # 스토리 재생성 (스토리 생성도 mock 필요 — OPENAI_API_KEY가 있으면 실제 호출 방지)
        with patch("app.services.generate.generate_story_with_gpt_or_dummy") as mock_story:
            # 더미 스토리 데이터 반환
            mock_story.return_value = {
                "title": "민준의 꿈 — 멋진 소방관",
                "pages": [
                    {"page": i + 1, "page_type": "title" if i == 0 else ("ending" if i == 23 else "content"),
                     "text": f"페이지 {i + 1}", "scene_description": f"Scene {i + 1}"}
                    for i in range(24)
                ],
            }
            client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=_auth_header(token),
            )

        # 새 페이지들에 대해 AI 일러스트가 다시 호출됨
        assert mock_illust.call_count == 24


# ──────────────────────────────────────────────
# 진행률 관련 테스트
# ──────────────────────────────────────────────

class TestGenerateProgress:
    """생성 진행률 정보 제공 테스트"""

    @patch("app.services.generate.generate_story_with_gpt_or_dummy")
    @patch("app.services.generate.generate_illustration_or_dummy")
    def test_generate_response_includes_total_pages(self, mock_illust, mock_story, client):
        """generate 응답에 총 페이지 수 정보 포함"""
        mock_illust.return_value = None
        mock_story.return_value = _dummy_story_data()

        token = _signup_and_login(client)
        book_id = _create_book_with_character(client, token)

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data["pages"]) == 24


# ──────────────────────────────────────────────
# 헬퍼 함수
# ──────────────────────────────────────────────

def _dummy_story_data(page_count=24):
    """더미 스토리 데이터를 반환한다 (mock용)."""
    pages = []
    for i in range(page_count):
        if i == 0:
            ptype = "title"
        elif i == page_count - 1:
            ptype = "ending"
        else:
            ptype = "content"
        pages.append({
            "page": i + 1,
            "page_type": ptype,
            "text": f"민준이가 소방관 활동을 하는 페이지 {i + 1}",
            "scene_description": f"Scene {i + 1}: A child firefighter in action",
        })
    return {"title": "민준의 꿈 — 멋진 소방관", "pages": pages}


def _signup_and_login(client, email="test@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "테스트", "phone": "01012345678"})
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _purchase_voucher(client, token, voucher_type="story_only"):
    res = client.post(
        "/api/vouchers/purchase",
        json={"voucher_type": voucher_type},
        headers=_auth_header(token),
    )
    return res.json()["id"]


def _create_book_with_character(client, token):
    """책 생성 + 필수 정보 설정 + 캐릭터 시트 확정까지"""
    voucher_id = _purchase_voucher(client, token)
    res = client.post(
        "/api/books",
        json={"voucher_id": voucher_id},
        headers=_auth_header(token),
    )
    book_id = res.json()["id"]

    # 필수 정보 설정
    client.patch(
        f"/api/books/{book_id}",
        json={
            "child_name": "민준",
            "job_name": "소방관",
            "job_category": "안전/보안",
            "art_style": "watercolor",
            "story_style": "dreaming_today",
            "page_count": 24,
            "plot_input": "소방관 이야기",
        },
        headers=_auth_header(token),
    )

    return book_id
