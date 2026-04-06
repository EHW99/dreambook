"""태스크 15: AI 스토리 생성 (GPT-4o) 테스트 — OpenAI API는 mock 사용"""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

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


def _create_book(client, token):
    voucher_id = _purchase_voucher(client, token)
    res = client.post(
        "/api/books",
        json={"voucher_id": voucher_id},
        headers=_auth_header(token),
    )
    return res.json()["id"]


def _setup_book(client, token, book_id, page_count=24, story_style="dreaming_today"):
    """필수 정보를 설정하여 generate 준비 상태로 만들기"""
    client.patch(
        f"/api/books/{book_id}",
        json={
            "child_name": "민준",
            "job_name": "소방관",
            "job_category": "안전/보안",
            "page_count": page_count,
            "plot_input": "소방관이 되어 마을을 지키는 이야기",
            "story_style": story_style,
            "art_style": "watercolor",
        },
        headers=_auth_header(token),
    )


def _make_mock_story_response(page_count=24):
    """GPT-4o mock 응답용 스토리 JSON 생성"""
    pages = []
    # title page
    pages.append({
        "page": 1,
        "page_type": "title",
        "text": "민준이의 꿈 — 멋진 소방관",
        "scene_description": "민준이가 소방관 모자를 쓰고 밝게 웃고 있는 모습",
    })
    # content pages
    content_count = page_count - 2
    for i in range(content_count):
        pages.append({
            "page": i + 2,
            "page_type": "content",
            "text": f"민준이는 소방관으로서 멋진 활동을 했어요. 장면 {i + 1}.",
            "scene_description": f"민준이가 소방관 활동을 하는 장면 {i + 1}",
        })
    # ending page
    pages.append({
        "page": page_count,
        "page_type": "ending",
        "text": "민준이는 멋진 소방관이 되어 모두를 지켰답니다. 끝.",
        "scene_description": "민준이가 밤하늘의 별을 바라보며 꿈을 꾸는 장면",
    })
    return {"title": "민준이의 꿈 — 멋진 소방관", "pages": pages}


# ──────────────────────────────────────────────
# ai_story 서비스 단위 테스트
# ──────────────────────────────────────────────

class TestAIStoryService:
    """ai_story.py 서비스 레벨 단위 테스트"""

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_returns_pages(self, mock_openai_class):
        """GPT-4o 호출 결과로 페이지 목록을 반환하는지"""
        from app.services.ai_story import generate_story_with_gpt

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # chat.completions.create 모킹
        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        result = generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="소방관이 되어 마을을 지키는 이야기",
            page_count=24,
            art_style="watercolor",
        )

        assert "title" in result
        assert "pages" in result
        assert len(result["pages"]) == 24
        # 각 페이지에 필수 필드가 있는지
        for page in result["pages"]:
            assert "text" in page
            assert "scene_description" in page
            assert "page_type" in page

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_calls_gpt4o(self, mock_openai_class):
        """GPT-4o 모델을 사용하는지 확인"""
        from app.services.ai_story import generate_story_with_gpt

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="소방관 이야기",
            page_count=24,
        )

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4o"

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_dreaming_today_style(self, mock_openai_class):
        """'꿈꾸는 오늘' 스타일 프롬프트에 시간/나이 언급 없이 생성"""
        from app.services.ai_story import generate_story_with_gpt

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="",
            page_count=24,
        )

        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        # 시스템/유저 메시지에 dreaming_today 관련 키워드가 포함되어야 함
        all_content = " ".join(m["content"] for m in messages)
        assert "민준" in all_content
        assert "소방관" in all_content
        # 스타일별 핵심 키워드 검증
        system_content = messages[0]["content"]
        assert "꿈이 이루어진 세계" in system_content

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_future_me_style(self, mock_openai_class):
        """'미래의 나' 스타일 프롬프트에 성장 과정 포함"""
        from app.services.ai_story import generate_story_with_gpt

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        generate_story_with_gpt(
            child_name="민준",
            job_name="의사",
            story_style="future_me",
            plot_input="",
            page_count=24,
            child_birth_date="2020-03-15",
        )

        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        all_content = " ".join(m["content"] for m in messages)
        assert "민준" in all_content
        assert "의사" in all_content
        # 스타일별 핵심 키워드 검증
        system_content = messages[0]["content"]
        assert "성장 과정" in system_content or "일대기" in system_content

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_art_style_in_prompt(self, mock_openai_class):
        """art_style이 프롬프트에 반영되는지 검증"""
        from app.services.ai_story import generate_story_with_gpt

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="",
            page_count=24,
            art_style="watercolor",
        )

        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        system_content = messages[0]["content"]
        assert "watercolor" in system_content

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_api_error_raises(self, mock_openai_class):
        """OpenAI API 오류 시 적절한 예외 발생"""
        from app.services.ai_story import generate_story_with_gpt, StoryGenerationError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        with pytest.raises(StoryGenerationError):
            generate_story_with_gpt(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,
            )

    @patch("app.services.ai_story.OpenAI")
    def test_generate_story_invalid_json_raises(self, mock_openai_class):
        """GPT가 잘못된 JSON을 반환하면 에러"""
        from app.services.ai_story import generate_story_with_gpt, StoryGenerationError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = "이것은 JSON이 아닙니다"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        with pytest.raises(StoryGenerationError):
            generate_story_with_gpt(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,
            )

    def test_fallback_to_dummy_when_no_api_key(self):
        """OPENAI_API_KEY가 없으면 더미 스토리 폴백"""
        from app.services.ai_story import generate_story_with_gpt_or_dummy

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            result = generate_story_with_gpt_or_dummy(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,
            )

            assert "title" in result
            assert "pages" in result
            assert len(result["pages"]) == 24

    @patch("app.services.ai_story.OpenAI")
    def test_response_missing_pages_key_raises(self, mock_openai_class):
        """GPT 응답에 pages 키가 없으면 StoryGenerationError 발생"""
        from app.services.ai_story import generate_story_with_gpt, StoryGenerationError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # pages 키가 없는 응답
        bad_response = {"title": "민준이의 꿈", "content": "잘못된 형식"}
        mock_message = MagicMock()
        mock_message.content = json.dumps(bad_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        with pytest.raises(StoryGenerationError, match="pages"):
            generate_story_with_gpt(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,
            )

    @patch("app.services.ai_story.OpenAI")
    def test_response_missing_title_uses_fallback(self, mock_openai_class):
        """GPT 응답에 title이 없으면 첫 페이지 텍스트로 대체"""
        from app.services.ai_story import generate_story_with_gpt

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # title 키가 없는 응답
        pages = _make_mock_story_response(24)["pages"]
        no_title_response = {"pages": pages}  # title 키 제외
        mock_message = MagicMock()
        mock_message.content = json.dumps(no_title_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        result = generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="",
            page_count=24,
        )

        # title은 첫 페이지 텍스트로 폴백
        assert result["title"] == pages[0]["text"]

    @patch("app.services.ai_story.OpenAI")
    def test_page_count_mismatch_logs_warning(self, mock_openai_class):
        """요청 페이지 수와 생성 페이지 수가 다르면 경고 로그"""
        from app.services.ai_story import generate_story_with_gpt

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 요청은 24페이지지만 20페이지만 반환
        mock_response = _make_mock_story_response(20)
        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion

        with patch("app.services.ai_story.logger") as mock_logger:
            result = generate_story_with_gpt(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,  # 24페이지 요청
            )

            # 경고 로그가 남는지 확인
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "24" in warning_msg
            assert "20" in warning_msg

        # 결과는 실제 생성된 페이지 수(20)를 반환
        assert len(result["pages"]) == 20


# ──────────────────────────────────────────────
# API 통합 테스트 (엔드포인트 레벨)
# ──────────────────────────────────────────────

class TestGenerateWithAI:
    """POST /api/books/:id/generate — AI 스토리 생성 통합 테스트"""

    @patch("app.services.ai_story.OpenAI")
    def test_generate_calls_ai_story(self, mock_openai_class, client):
        """generate 엔드포인트가 AI 스토리 서비스를 호출하는지"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        mock_response = _make_mock_story_response(24)
        mock_client_instance = MagicMock()
        mock_openai_class.return_value = mock_client_instance

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_completion

        # settings에서 OPENAI_API_KEY 설정
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "editing"
        assert len(data["pages"]) == 24

    def test_generate_fallback_dummy_without_api_key(self, client):
        """OPENAI_API_KEY 없으면 더미 폴백으로 정상 동작"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "editing"
        assert len(data["pages"]) == 24

    @patch("app.services.ai_story.OpenAI")
    def test_generate_ai_error_returns_500(self, mock_openai_class, client):
        """AI 호출 실패 시 적절한 에러 응답"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        mock_client_instance = MagicMock()
        mock_openai_class.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.side_effect = Exception("Timeout")

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        # AI 실패 시 500 또는 적절한 에러 반환
        assert res.status_code == 500
        assert "스토리 생성" in res.json()["detail"]


class TestRegenerateStoryWithAI:
    """POST /api/books/:id/regenerate-story — AI 스토리 재생성"""

    def _generate_first(self, client, token, book_id):
        """첫 번째 생성 (더미 폴백)"""
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""
            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )
        assert res.status_code == 200

    def test_regenerate_story_increments_count(self, client):
        """재생성 시 story_regen_count 증가"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)
        self._generate_first(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            res = client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=_auth_header(token),
            )

        assert res.status_code == 200
        data = res.json()
        assert data["story_regen_count"] == 1

    def test_regenerate_story_max_3_times(self, client):
        """최대 3회 재생성 제한"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)
        self._generate_first(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            # 3회 재생성
            for i in range(3):
                res = client.post(
                    f"/api/books/{book_id}/regenerate-story",
                    headers=_auth_header(token),
                )
                assert res.status_code == 200

            # 4번째 재생성 시도 → 422
            res = client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=_auth_header(token),
            )
            assert res.status_code == 422
            assert "재생성 횟수" in res.json()["detail"]

    @patch("app.services.ai_story.OpenAI")
    def test_regenerate_story_calls_ai(self, mock_openai_class, client):
        """재생성 시에도 AI 호출"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)
        # 첫 생성 (더미)
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""
            client.post(f"/api/books/{book_id}/generate", headers=_auth_header(token))

        # 재생성 시 AI 호출
        mock_response = _make_mock_story_response(24)
        mock_client_instance = MagicMock()
        mock_openai_class.return_value = mock_client_instance

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_completion

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"

            res = client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=_auth_header(token),
            )

        assert res.status_code == 200
        assert len(res.json()["pages"]) == 24


class TestGenerateStoryPageContent:
    """생성된 스토리 내용 검증"""

    def test_each_page_has_scene_description(self, client):
        """모든 페이지에 scene_description이 있어야 함"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        data = res.json()
        for page in data["pages"]:
            assert page["scene_description"] is not None
            assert len(page["scene_description"]) > 0

    def test_title_page_exists(self, client):
        """제목 페이지가 존재"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        data = res.json()
        title_pages = [p for p in data["pages"] if p["page_type"] == "title"]
        assert len(title_pages) == 1

    def test_ending_page_exists(self, client):
        """엔딩 페이지가 존재"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        data = res.json()
        ending_pages = [p for p in data["pages"] if p["page_type"] == "ending"]
        assert len(ending_pages) == 1


class TestAIStoryTimeout:
    """타임아웃 처리 테스트"""

    @patch("app.services.ai_story.OpenAI")
    def test_timeout_error_handled(self, mock_openai_class, client):
        """OpenAI 타임아웃 시 적절한 에러"""
        import httpx

        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        _setup_book(client, token, book_id)

        mock_client_instance = MagicMock()
        mock_openai_class.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.side_effect = Exception(
            "Request timed out"
        )

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = "test-key"

            res = client.post(
                f"/api/books/{book_id}/generate",
                headers=_auth_header(token),
            )

        assert res.status_code == 500
        assert "스토리 생성" in res.json()["detail"]
