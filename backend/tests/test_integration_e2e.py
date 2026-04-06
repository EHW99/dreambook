"""태스크 18: AI 생성 통합 테스트 + 성향 테스트 + 비용 모니터링

모든 AI 호출은 mock — 실제 OpenAI API 호출 없음.
"""
import json
import pytest
from unittest.mock import patch, MagicMock


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def _signup_and_login(client, email="e2e@example.com"):
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "테스트", "phone": "01012345678"})
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _purchase_voucher(client, token, voucher_type="story_and_print"):
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


def _make_mock_story_response(page_count=24):
    pages = []
    pages.append({
        "page": 1,
        "page_type": "title",
        "text": "민준이의 꿈 — 멋진 소방관",
        "scene_description": "A child wearing firefighter helmet, smiling",
    })
    for i in range(page_count - 2):
        pages.append({
            "page": i + 2,
            "page_type": "content",
            "text": f"민준이는 소방관으로서 멋진 활동을 했어요. 장면 {i + 1}.",
            "scene_description": f"Scene {i + 1}: child firefighter in action",
        })
    pages.append({
        "page": page_count,
        "page_type": "ending",
        "text": "민준이는 멋진 소방관이 되어 모두를 지켰답니다. 끝.",
        "scene_description": "Child looking at starry sky, peaceful scene",
    })
    return {"title": "민준이의 꿈 — 멋진 소방관", "pages": pages}


# ──────────────────────────────────────────────
# E2E 통합 테스트 (전체 흐름)
# ──────────────────────────────────────────────

class TestE2EWizardFlow:
    """정보 입력 → 직업 → 스타일 → 그림체 → 캐릭터 → 확정 → 줄거리 → AI 생성 → 편집 → 주문 전체 흐름"""

    def test_full_wizard_flow_with_mock_ai(self, client):
        """전체 위자드 흐름이 동작하는지 확인 (mock AI)"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)
        headers = _auth_header(token)

        # Step 1: 정보 입력
        res = client.patch(f"/api/books/{book_id}", json={
            "child_name": "민준",
            "child_birth_date": "2020-03-15",
            "current_step": 2,
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["child_name"] == "민준"

        # Step 2: 직업 선택
        res = client.patch(f"/api/books/{book_id}", json={
            "job_category": "안전/봉사",
            "job_name": "소방관",
            "current_step": 3,
        }, headers=headers)
        assert res.status_code == 200

        # Step 3: 동화 스타일
        res = client.patch(f"/api/books/{book_id}", json={
            "story_style": "dreaming_today",
            "current_step": 4,
        }, headers=headers)
        assert res.status_code == 200

        # Step 4: 그림체
        res = client.patch(f"/api/books/{book_id}", json={
            "art_style": "watercolor",
            "current_step": 5,
        }, headers=headers)
        assert res.status_code == 200

        # Step 5: 캐릭터 생성 (mock) + 확정
        res = client.post(f"/api/books/{book_id}/character", headers=headers)
        assert res.status_code in (200, 201)
        char_data = res.json()
        char_id = char_data["id"]

        # 캐릭터 선택 (확정)
        res = client.patch(
            f"/api/books/{book_id}/character/{char_id}/select",
            headers=headers,
        )
        assert res.status_code == 200

        # Step 5 → 6 전환
        res = client.patch(f"/api/books/{book_id}", json={
            "current_step": 6,
            "status": "character_confirmed",
        }, headers=headers)
        assert res.status_code == 200

        # Step 6: 옵션 선택
        res = client.patch(f"/api/books/{book_id}", json={
            "page_count": 24,
            "book_spec_uid": "SQUAREBOOK_HC",
            "current_step": 7,
        }, headers=headers)
        assert res.status_code == 200

        # Step 7: 줄거리 입력 (테마 반영)
        res = client.patch(f"/api/books/{book_id}", json={
            "plot_input": "소방관이 된 주인공이 신비로운 모험을 떠나요.",
            "current_step": 8,
        }, headers=headers)
        assert res.status_code == 200
        assert "모험" in res.json()["plot_input"]

        # Step 8: AI 스토리 + 이미지 생성 (mock)
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""
            res = client.post(f"/api/books/{book_id}/generate", headers=headers)

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "editing"
        assert len(data["pages"]) == 24

        # Step 9: 편집 — 텍스트 수정
        pages_res = client.get(f"/api/books/{book_id}/pages", headers=headers)
        assert pages_res.status_code == 200
        pages = pages_res.json()
        first_page = pages[1]  # content page

        res = client.patch(
            f"/api/books/{book_id}/pages/{first_page['id']}",
            json={"text_content": "수정된 텍스트입니다."},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["text_content"] == "수정된 텍스트입니다."

        # 책 상태 확인
        book_res = client.get(f"/api/books/{book_id}", headers=headers)
        assert book_res.status_code == 200
        assert book_res.json()["status"] == "editing"
        assert book_res.json()["title"] is not None


class TestThemePlotIntegration:
    """스토리 테마 카드 → 줄거리 → AI 스토리 생성 연결 테스트"""

    def test_adventure_theme_plot_in_generation(self, client):
        """모험 테마 줄거리가 AI 스토리 생성에 반영되는지"""
        token = _signup_and_login(client, "theme@example.com")
        book_id = _create_book(client, token)
        headers = _auth_header(token)

        # 필수 정보 설정
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "서연",
            "job_name": "의사",
            "job_category": "의료/과학",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
            "page_count": 24,
        }, headers=headers)

        # 테마 기반 줄거리 설정
        adventure_plot = "의사가 된 주인공이 신비로운 모험을 떠나요. 낯선 곳에서 어려운 문제를 만나지만, 용기를 내어 해결하고 멋진 의사로 성장하는 이야기예요."
        client.patch(f"/api/books/{book_id}", json={
            "plot_input": adventure_plot,
        }, headers=headers)

        # 생성 (더미 폴백)
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""
            res = client.post(f"/api/books/{book_id}/generate", headers=headers)

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "editing"
        assert len(data["pages"]) == 24

        # 책 정보에 줄거리가 저장되었는지
        book_res = client.get(f"/api/books/{book_id}", headers=headers)
        assert "모험" in book_res.json()["plot_input"]

    def test_helping_theme_plot(self, client):
        """도움 테마 줄거리 설정 및 저장"""
        token = _signup_and_login(client, "helping@example.com")
        book_id = _create_book(client, token)
        headers = _auth_header(token)

        helping_plot = "소방관이 된 주인공이 도움이 필요한 사람들을 만나요."
        res = client.patch(f"/api/books/{book_id}", json={
            "child_name": "지우",
            "job_name": "소방관",
            "plot_input": helping_plot,
        }, headers=headers)

        assert res.status_code == 200
        assert "도움" in res.json()["plot_input"]


class TestRegeneration:
    """재생성 전체 흐름 테스트"""

    def _setup_and_generate(self, client, email="regen@example.com"):
        token = _signup_and_login(client, email)
        book_id = _create_book(client, token)
        headers = _auth_header(token)

        # 필수 정보 설정
        client.patch(f"/api/books/{book_id}", json={
            "child_name": "하은",
            "job_name": "과학자",
            "job_category": "의료/과학",
            "page_count": 24,
            "plot_input": "과학자 이야기",
            "story_style": "dreaming_today",
            "art_style": "crayon",
        }, headers=headers)

        # 캐릭터 생성 + 확정
        res = client.post(f"/api/books/{book_id}/character", headers=headers)
        char_id = res.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=headers)

        # 생성
        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""
            res = client.post(f"/api/books/{book_id}/generate", headers=headers)

        assert res.status_code == 200
        return token, book_id, headers

    def test_character_regeneration_max_4(self, client):
        """캐릭터 재생성 최대 4회 제한"""
        token = _signup_and_login(client, "charregen@example.com")
        book_id = _create_book(client, token)
        headers = _auth_header(token)

        client.patch(f"/api/books/{book_id}", json={
            "child_name": "민서",
            "job_name": "화가",
            "art_style": "watercolor",
        }, headers=headers)

        # 첫 생성
        res = client.post(f"/api/books/{book_id}/character", headers=headers)
        assert res.status_code in (200, 201)

        # 4회 재생성
        for i in range(4):
            res = client.post(f"/api/books/{book_id}/character", headers=headers)
            assert res.status_code in (200, 201), f"재생성 {i + 1}회 실패"

        # 5번째 시도 — 제한 초과
        res = client.post(f"/api/books/{book_id}/character", headers=headers)
        assert res.status_code == 422

    def test_story_regeneration_max_3(self, client):
        """스토리 재생성 최대 3회 제한"""
        token, book_id, headers = self._setup_and_generate(client, "storyregen@example.com")

        with patch("app.services.ai_story.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            # 3회 재생성
            for i in range(3):
                res = client.post(
                    f"/api/books/{book_id}/regenerate-story",
                    headers=headers,
                )
                assert res.status_code == 200, f"재생성 {i + 1}회 실패"

            # 4번째 시도 — 제한 초과
            res = client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=headers,
            )
            assert res.status_code == 422
            assert "재생성 횟수" in res.json()["detail"]

    def test_image_regeneration_max_4_per_page(self, client):
        """이미지 재생성 페이지당 최대 4회 제한"""
        token, book_id, headers = self._setup_and_generate(client, "imgregen@example.com")

        # 페이지 목록 조회
        pages_res = client.get(f"/api/books/{book_id}/pages", headers=headers)
        page_id = pages_res.json()[1]["id"]  # content page

        with patch("app.services.ai_illustration.get_settings") as mock_settings:
            mock_settings.return_value.OPENAI_API_KEY = ""

            # 4회 재생성
            for i in range(4):
                res = client.post(
                    f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
                    headers=headers,
                )
                assert res.status_code == 200, f"이미지 재생성 {i + 1}회 실패"

            # 5번째 시도 — 제한 초과
            res = client.post(
                f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
                headers=headers,
            )
            assert res.status_code == 422
            assert "재생성 횟수" in res.json()["detail"]


# ──────────────────────────────────────────────
# 성향 테스트 API 테스트
# ──────────────────────────────────────────────

class TestAptitudeTestAPI:
    """성향 테스트 API 테스트"""

    def test_get_questions(self, client):
        """질문 목록 조회"""
        res = client.get("/api/aptitude/questions")
        assert res.status_code == 200
        questions = res.json()
        assert len(questions) == 5
        for q in questions:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert len(q["options"]) == 4

    def test_get_result_safety_service(self, client):
        """안전/봉사 직업 추천"""
        answers = {1: "a", 2: "c", 3: "d", 4: "c", 5: "a"}
        res = client.post("/api/aptitude/result", json={"answers": answers})
        assert res.status_code == 200
        data = res.json()
        assert "category_id" in data
        assert "category_name" in data
        assert "recommended_jobs" in data
        assert len(data["recommended_jobs"]) == 2
        assert "scores" in data

    def test_get_result_arts_culture(self, client):
        """예술/문화 직업 추천"""
        answers = {1: "d", 2: "b", 3: "c", 4: "b", 5: "d"}
        res = client.post("/api/aptitude/result", json={"answers": answers})
        assert res.status_code == 200
        data = res.json()
        assert data["category_id"] == "arts_culture"
        assert data["category_name"] == "예술/문화"

    def test_get_result_tech_engineering(self, client):
        """기술/공학 직업 추천"""
        answers = {1: "b", 2: "a", 3: "b", 4: "d", 5: "b"}
        res = client.post("/api/aptitude/result", json={"answers": answers})
        assert res.status_code == 200
        data = res.json()
        assert data["category_id"] == "tech_engineering"

    def test_get_result_medical_science(self, client):
        """의료/과학 직업 추천"""
        answers = {1: "c", 2: "d", 3: "a", 4: "a", 5: "c"}
        res = client.post("/api/aptitude/result", json={"answers": answers})
        assert res.status_code == 200
        data = res.json()
        assert data["category_id"] == "medical_science"

    def test_partial_answers(self, client):
        """부분 답변도 결과 반환"""
        answers = {1: "a", 2: "c"}
        res = client.post("/api/aptitude/result", json={"answers": answers})
        assert res.status_code == 200
        data = res.json()
        assert "category_id" in data

    def test_empty_answers(self, client):
        """빈 답변도 결과 반환 (기본값)"""
        res = client.post("/api/aptitude/result", json={"answers": {}})
        assert res.status_code == 200

    def test_no_auth_required(self, client):
        """인증 없이 접근 가능"""
        res = client.get("/api/aptitude/questions")
        assert res.status_code == 200

        res = client.post("/api/aptitude/result", json={"answers": {1: "a"}})
        assert res.status_code == 200


# ──────────────────────────────────────────────
# 비용 모니터링 테스트
# ──────────────────────────────────────────────

class TestCostMonitoring:
    """비용 모니터링 로깅 테스트"""

    def test_cost_monitor_story_logging(self):
        """스토리 생성 비용 로깅"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        monitor.log_story_call(
            prompt_tokens=500,
            completion_tokens=1000,
            total_tokens=1500,
            success=True,
        )

        assert monitor.stats.story_calls == 1
        assert monitor.stats.story_tokens == 1500
        assert len(monitor.records) == 1
        assert monitor.records[0].service == "story"
        assert monitor.records[0].model == "gpt-4o"

    def test_cost_monitor_character_logging(self):
        """캐릭터 생성 비용 로깅"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        monitor.log_character_call(image_count=1, success=True)

        assert monitor.stats.character_calls == 1
        assert monitor.stats.character_images == 1

    def test_cost_monitor_illustration_logging(self):
        """일러스트 생성 비용 로깅"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        monitor.log_illustration_call(image_count=1, success=True)
        monitor.log_illustration_call(image_count=1, success=True)

        assert monitor.stats.illustration_calls == 2
        assert monitor.stats.illustration_images == 2

    def test_cost_monitor_error_tracking(self):
        """에러 카운트 추적"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        monitor.log_story_call(success=False, error="API timeout")
        monitor.log_character_call(success=False, error="Content policy")

        assert monitor.stats.total_errors == 2
        assert monitor.stats.story_calls == 1
        assert monitor.stats.character_calls == 1

    def test_cost_monitor_summary(self):
        """비용 모니터링 요약"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        monitor.log_story_call(total_tokens=1000, success=True)
        monitor.log_character_call(image_count=1, success=True)
        monitor.log_illustration_call(image_count=3, success=True)

        summary = monitor.get_summary()
        assert summary["story"]["calls"] == 1
        assert summary["story"]["total_tokens"] == 1000
        assert summary["character"]["calls"] == 1
        assert summary["illustration"]["calls"] == 1
        assert summary["illustration"]["total_images"] == 3
        assert summary["total_errors"] == 0

    def test_cost_monitor_reset(self):
        """통계 초기화"""
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.log_story_call(total_tokens=500, success=True)
        monitor.reset()

        assert monitor.stats.story_calls == 0
        assert monitor.stats.story_tokens == 0
        assert len(monitor.records) == 0

    @patch("app.services.ai_story.OpenAI")
    def test_story_generation_logs_cost(self, mock_openai_class):
        """AI 스토리 생성 시 비용 모니터에 기록되는지"""
        from app.services.ai_story import generate_story_with_gpt
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        mock_response = _make_mock_story_response(24)
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = json.dumps(mock_response, ensure_ascii=False)
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        # usage 정보 모킹
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 200
        mock_usage.completion_tokens = 800
        mock_usage.total_tokens = 1000
        mock_completion.usage = mock_usage
        mock_client.chat.completions.create.return_value = mock_completion

        generate_story_with_gpt(
            child_name="민준",
            job_name="소방관",
            story_style="dreaming_today",
            plot_input="소방관 이야기",
            page_count=24,
        )

        assert monitor.stats.story_calls == 1
        assert monitor.stats.story_tokens == 1000

    @patch("app.services.ai_story.OpenAI")
    def test_story_generation_failure_logs_error(self, mock_openai_class):
        """AI 스토리 생성 실패 시에도 비용 모니터에 기록"""
        from app.services.ai_story import generate_story_with_gpt, StoryGenerationError
        from app.services.cost_monitor import CostMonitor

        monitor = CostMonitor()
        monitor.reset()

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Timeout")

        with pytest.raises(StoryGenerationError):
            generate_story_with_gpt(
                child_name="민준",
                job_name="소방관",
                story_style="dreaming_today",
                plot_input="",
                page_count=24,
            )

        assert monitor.stats.story_calls == 1
        assert monitor.stats.total_errors == 1


# ──────────────────────────────────────────────
# 성향 테스트 서비스 단위 테스트
# ──────────────────────────────────────────────

class TestAptitudeService:
    """aptitude_test.py 서비스 레벨 단위 테스트"""

    def test_get_questions_returns_5(self):
        from app.services.aptitude_test import get_aptitude_questions
        questions = get_aptitude_questions()
        assert len(questions) == 5

    def test_each_question_has_4_options(self):
        from app.services.aptitude_test import get_aptitude_questions
        for q in get_aptitude_questions():
            assert len(q["options"]) == 4

    def test_calculate_all_safety(self):
        """모든 답변이 안전/봉사를 가리킬 때"""
        from app.services.aptitude_test import calculate_aptitude_result
        answers = {1: "a", 2: "c", 3: "d", 4: "c", 5: "a"}
        result = calculate_aptitude_result(answers)
        assert result["category_id"] == "safety_service"
        assert result["category_name"] == "안전/봉사"
        assert len(result["recommended_jobs"]) == 2

    def test_calculate_all_arts(self):
        """모든 답변이 예술/문화를 가리킬 때"""
        from app.services.aptitude_test import calculate_aptitude_result
        answers = {1: "d", 2: "b", 3: "c", 4: "b", 5: "d"}
        result = calculate_aptitude_result(answers)
        assert result["category_id"] == "arts_culture"

    def test_calculate_empty_answers(self):
        """빈 답변 시 기본 카테고리 반환"""
        from app.services.aptitude_test import calculate_aptitude_result
        result = calculate_aptitude_result({})
        assert "category_id" in result
        assert "recommended_jobs" in result

    def test_scores_dict_has_all_categories(self):
        """점수 딕셔너리에 모든 카테고리가 있는지"""
        from app.services.aptitude_test import calculate_aptitude_result
        result = calculate_aptitude_result({1: "a"})
        assert "medical_science" in result["scores"]
        assert "arts_culture" in result["scores"]
        assert "safety_service" in result["scores"]
        assert "tech_engineering" in result["scores"]
        assert "education_sports" in result["scores"]
