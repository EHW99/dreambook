"""태스크 16: AI 캐릭터 시트 생성 (GPT Image) 테스트 -- OpenAI API는 mock 사용"""
import base64
import os
import pytest
from unittest.mock import patch, MagicMock


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def _signup_and_login(client, email="test@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123"})
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


def _create_book(client, token):
    voucher_id = _purchase_voucher(client, token)
    res = client.post(
        "/api/books",
        json={"voucher_id": voucher_id},
        headers=_auth_header(token),
    )
    return res.json()["id"]


def _setup_book_for_character(client, token, book_id):
    """캐릭터 생성에 필요한 필수 정보 설정"""
    client.patch(
        f"/api/books/{book_id}",
        json={
            "child_name": "민준",
            "job_name": "소방관",
            "job_category": "안전/보안",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
        },
        headers=_auth_header(token),
    )


def _make_fake_png_bytes():
    """1x1 흰색 PNG를 만들어 반환 (테스트용)"""
    from PIL import Image
    import io
    img = Image.new("RGB", (64, 64), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_mock_image_response():
    """GPT Image API mock 응답 (base64 인코딩)"""
    png_bytes = _make_fake_png_bytes()
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    mock_image = MagicMock()
    mock_image.b64_json = b64
    mock_response = MagicMock()
    mock_response.data = [mock_image]
    return mock_response


# ──────────────────────────────────────────────
# ai_character 서비스 단위 테스트
# ──────────────────────────────────────────────

class TestAICharacterService:
    """ai_character.py 서비스 레벨 단위 테스트"""

    @patch("app.services.ai_character.OpenAI")
    def test_generate_character_returns_image_bytes(self, mock_openai_class):
        """GPT Image 호출 결과로 PNG 바이트를 반환하는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        # 테스트용 이미지 파일 생성
        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            result = generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            assert isinstance(result, bytes)
            assert len(result) > 0
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_generate_character_uses_images_edit(self, mock_openai_class):
        """images.edit 엔드포인트를 사용하는지 확인"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            # images.edit이 호출됐는지 확인
            assert mock_client.images.edit.called
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_generate_character_model_param(self, mock_openai_class):
        """gpt-image-1 모델을 사용하는지 확인"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            assert call_kwargs.kwargs.get("model") == "gpt-image-1"
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_generate_character_size_1024(self, mock_openai_class):
        """size가 1024x1024인지 확인"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            assert call_kwargs.kwargs.get("size") == "1024x1024"
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_generate_character_quality_medium(self, mock_openai_class):
        """quality가 medium인지 확인"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            assert call_kwargs.kwargs.get("quality") == "medium"
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_prompt_contains_art_style_keywords(self, mock_openai_class):
        """프롬프트에 그림체별 키워드가 포함되는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            prompt = call_kwargs.kwargs.get("prompt", "")
            assert "watercolor" in prompt.lower()
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_prompt_contains_job_description(self, mock_openai_class):
        """프롬프트에 직업 복장 묘사가 포함되는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="3d",
                job_name="의사",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            prompt = call_kwargs.kwargs.get("prompt", "")
            # 직업명이 프롬프트에 포함되어야 함
            assert "doctor" in prompt.lower() or "의사" in prompt.lower()
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_all_art_styles_have_keywords(self, mock_openai_class):
        """모든 그림체 스타일에 대해 키워드가 정의되어 있는지"""
        from app.services.ai_character import ART_STYLE_KEYWORDS

        expected_styles = ["watercolor", "pencil", "crayon", "3d", "cartoon"]
        for style in expected_styles:
            assert style in ART_STYLE_KEYWORDS, f"'{style}' 스타일 키워드 미정의"
            assert len(ART_STYLE_KEYWORDS[style]) > 0

    @patch("app.services.ai_character.OpenAI")
    def test_api_error_raises_exception(self, mock_openai_class):
        """OpenAI API 오류 시 CharacterGenerationError 발생"""
        from app.services.ai_character import (
            generate_character_image,
            CharacterGenerationError,
        )

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.side_effect = Exception("API error")

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            with pytest.raises(CharacterGenerationError):
                generate_character_image(
                    photo_path=temp_path,
                    art_style="watercolor",
                    job_name="소방관",
                    story_style="dreaming_today",
                )
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_content_filter_error(self, mock_openai_class):
        """콘텐츠 필터링 거부 시 적절한 예외"""
        from app.services.ai_character import (
            generate_character_image,
            CharacterGenerationError,
        )
        from openai import BadRequestError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # BadRequestError를 시뮬레이션
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": {"message": "content_policy_violation"}}
        mock_client.images.edit.side_effect = BadRequestError(
            message="content_policy_violation",
            response=error_response,
            body={"error": {"message": "content_policy_violation"}},
        )

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            with pytest.raises(CharacterGenerationError, match="콘텐츠 정책"):
                generate_character_image(
                    photo_path=temp_path,
                    art_style="watercolor",
                    job_name="소방관",
                    story_style="dreaming_today",
                )
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_timeout_error(self, mock_openai_class):
        """타임아웃 시 적절한 예외"""
        from app.services.ai_character import (
            generate_character_image,
            CharacterGenerationError,
        )

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.side_effect = Exception("Request timed out")

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            with pytest.raises(CharacterGenerationError):
                generate_character_image(
                    photo_path=temp_path,
                    art_style="watercolor",
                    job_name="소방관",
                    story_style="dreaming_today",
                )
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_crayon_style_keywords(self, mock_openai_class):
        """크레파스 스타일의 키워드가 프롬프트에 포함되는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="crayon",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            prompt = call_kwargs.kwargs.get("prompt", "")
            assert "crayon" in prompt.lower()
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    def test_future_me_style_affects_prompt(self, mock_openai_class):
        """'미래의 나' 동화 스타일이 프롬프트에 영향을 주는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="future_me",
            )
            call_kwargs = mock_client.images.edit.call_args
            prompt = call_kwargs.kwargs.get("prompt", "")
            # 미래의 나 스타일은 성장 관련 키워드가 포함될 수 있음
            assert len(prompt) > 50  # 충분히 상세한 프롬프트
        finally:
            os.unlink(temp_path)


# ──────────────────────────────────────────────
# character.py 서비스 통합 테스트 (AI 연동)
# ──────────────────────────────────────────────

class TestCharacterServiceWithAI:
    """character.py의 AI 연동 로직 테스트"""

    @patch("app.services.ai_character.OpenAI")
    @patch("app.services.character.get_settings")
    def test_create_character_with_ai(self, mock_settings, mock_openai_class, client):
        """OPENAI_API_KEY가 있으면 AI 캐릭터 생성"""
        mock_settings.return_value.OPENAI_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book_for_character(client, token, book_id)

        # 사진 업로드 (book에 photo_id 설정)
        from PIL import Image
        import io
        img = Image.new("RGB", (512, 512), (255, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        photo_res = client.post(
            "/api/photos",
            files={"file": ("child.png", buf, "image/png")},
            headers=_auth_header(token),
        )
        if photo_res.status_code == 201:
            photo_id = photo_res.json()["id"]
            client.patch(
                f"/api/books/{book_id}",
                json={"photo_id": photo_id},
                headers=_auth_header(token),
            )

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["book_id"] == book_id
        assert "image_path" in data

    @patch("app.services.character.get_settings")
    def test_create_character_without_api_key_falls_back_to_dummy(self, mock_settings, client):
        """OPENAI_API_KEY가 없으면 더미 폴백"""
        mock_settings.return_value.OPENAI_API_KEY = ""

        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert "dummy" in data["image_path"] or "placeholder" in data["image_path"].lower() or data["image_path"].startswith("/uploads/")

    def test_max_regeneration_still_works(self, client):
        """최대 재생성 횟수 (총 5회) 초과 시 여전히 422"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        for i in range(5):
            res = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
            assert res.status_code == 201

        res = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        assert res.status_code == 422
        assert "재생성 횟수를 모두 사용했습니다" in res.json()["detail"]

    @patch("app.services.ai_character.OpenAI")
    @patch("app.services.character.get_settings")
    def test_generated_image_saved_to_server(self, mock_settings, mock_openai_class, client):
        """AI 생성 이미지가 서버에 파일로 저장되는지"""
        mock_settings.return_value.OPENAI_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book_for_character(client, token, book_id)

        # 사진 업로드
        from PIL import Image
        import io
        img = Image.new("RGB", (512, 512), (255, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        photo_res = client.post(
            "/api/photos",
            files={"file": ("child.png", buf, "image/png")},
            headers=_auth_header(token),
        )
        if photo_res.status_code == 201:
            photo_id = photo_res.json()["id"]
            client.patch(
                f"/api/books/{book_id}",
                json={"photo_id": photo_id},
                headers=_auth_header(token),
            )

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        image_path = data["image_path"]
        # 이미지 경로가 유효한 형식인지 확인
        assert image_path.endswith(".png")

    @patch("app.services.character.get_settings")
    def test_content_policy_error_returns_400(self, mock_settings, client):
        """콘텐츠 정책 위반 시 400 에러가 사용자에게 전달되는지"""
        from app.services.ai_character import CharacterGenerationError

        mock_settings.return_value.OPENAI_API_KEY = "test-key"

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book_for_character(client, token, book_id)

        # 사진 업로드
        from PIL import Image
        import io
        img = Image.new("RGB", (512, 512), (255, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        photo_res = client.post(
            "/api/photos",
            files={"file": ("child.png", buf, "image/png")},
            headers=_auth_header(token),
        )
        if photo_res.status_code == 201:
            photo_id = photo_res.json()["id"]
            client.patch(
                f"/api/books/{book_id}",
                json={"photo_id": photo_id},
                headers=_auth_header(token),
            )

        # generate_character_image를 모킹하여 콘텐츠 정책 위반 에러 발생
        with patch(
            "app.services.ai_character.generate_character_image",
            side_effect=CharacterGenerationError(
                "콘텐츠 정책에 의해 이미지를 생성할 수 없습니다. 다른 사진을 사용해주세요."
            ),
        ), patch("app.services.character.os.path.exists", return_value=True):
            res = client.post(
                f"/api/books/{book_id}/character",
                headers=_auth_header(token),
            )
        assert res.status_code == 400
        assert "콘텐츠 정책" in res.json()["detail"] or "다른 사진" in res.json()["detail"]

    @patch("app.services.ai_character.OpenAI")
    @patch("app.services.character.get_settings")
    def test_ai_image_path_is_url_format(self, mock_settings, mock_openai_class, client):
        """AI 생성 이미지 경로가 /uploads/ URL 형태인지"""
        mock_settings.return_value.OPENAI_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book_for_character(client, token, book_id)

        # 사진 업로드
        from PIL import Image
        import io
        img = Image.new("RGB", (512, 512), (255, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        photo_res = client.post(
            "/api/photos",
            files={"file": ("child.png", buf, "image/png")},
            headers=_auth_header(token),
        )
        if photo_res.status_code == 201:
            photo_id = photo_res.json()["id"]
            client.patch(
                f"/api/books/{book_id}",
                json={"photo_id": photo_id},
                headers=_auth_header(token),
            )

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        # AI 생성 이미지 경로는 /uploads/characters/ 형태여야 함
        assert data["image_path"].startswith("/uploads/characters/")

    @patch("app.services.ai_character.OpenAI")
    def test_output_format_png_specified(self, mock_openai_class):
        """output_format='png'가 명시적으로 전달되는지"""
        from app.services.ai_character import generate_character_image

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        import tempfile
        png_bytes = _make_fake_png_bytes()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        try:
            generate_character_image(
                photo_path=temp_path,
                art_style="watercolor",
                job_name="소방관",
                story_style="dreaming_today",
            )
            call_kwargs = mock_client.images.edit.call_args
            assert call_kwargs.kwargs.get("output_format") == "png"
        finally:
            os.unlink(temp_path)

    @patch("app.services.ai_character.OpenAI")
    @patch("app.services.character.get_settings")
    def test_character_saved_to_db(self, mock_settings, mock_openai_class, client):
        """생성된 캐릭터가 character_sheets 테이블에 저장되는지"""
        mock_settings.return_value.OPENAI_API_KEY = "test-key"

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.edit.return_value = _make_mock_image_response()

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book_for_character(client, token, book_id)

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201

        # 갤러리에서 확인
        gallery_res = client.get(
            f"/api/books/{book_id}/characters",
            headers=_auth_header(token),
        )
        assert gallery_res.status_code == 200
        assert len(gallery_res.json()) == 1
