"""태스크 8: 동화책 옵션/줄거리/생성 API 테스트"""
import pytest


def _signup_and_login(client, email="test@example.com"):
    """헬퍼: 회원가입 + 로그인하여 토큰 반환"""
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


class TestBookUpdateOptions:
    """PATCH /api/books/:id — 옵션/줄거리 저장"""

    def test_update_page_count(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 30},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["page_count"] == 30

    def test_update_page_count_must_be_even(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 25},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_page_count_minimum_24(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 22},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_book_spec_uid(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"book_spec_uid": "PHOTOBOOK_A4_SC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["book_spec_uid"] == "PHOTOBOOK_A4_SC"

    def test_update_invalid_book_spec_uid(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"book_spec_uid": "INVALID_SPEC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_plot_input(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"plot_input": "소방관이 되어 마을을 지키는 이야기"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["plot_input"] == "소방관이 되어 마을을 지키는 이야기"


class TestBookGenerate:
    """POST /api/books/:id/generate — 더미 스토리+이미지 생성"""

    def test_generate_creates_pages(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 필수 정보 설정 (current_step 변경 없이 데이터만 저장)
        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "editing"
        assert "pages" in data
        # 페이지 수 = page_count (Book Print API는 1회 호출 = 1페이지)
        # title(1) + content(22) + ending(1) = 24
        assert len(data["pages"]) == 24

    def test_generate_page_has_text_and_image(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "김철수",
                "job_name": "의사",
                "job_category": "의료/과학",
                "page_count": 24,
                "plot_input": "의사 이야기",
            },
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        data = res.json()
        # 각 페이지에 text_content가 있어야 함
        for page in data["pages"]:
            assert page["text_content"] is not None
            assert len(page["text_content"]) > 0
            # 각 페이지에 이미지가 있어야 함
            assert len(page["images"]) >= 1

    def test_generate_substitutes_name_and_job(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        data = res.json()
        # 더미 스토리에 아이 이름과 직업이 포함되어야 함
        all_text = " ".join(p["text_content"] for p in data["pages"])
        assert "홍길동" in all_text
        assert "소방관" in all_text

    def test_generate_sets_book_status_to_editing(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )

        # 책 상태 확인
        res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.json()["status"] == "editing"
        assert res.json()["current_step"] == 9

    def test_generate_requires_child_name(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # child_name 없이 생성 시도
        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_generate_requires_job_name(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={"child_name": "홍길동"},
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_generate_other_user_forbidden(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_book(client, token1)

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_generate_nonexistent_book(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/books/9999/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_generate_sets_title(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )

        res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.json()["title"] is not None
        assert len(res.json()["title"]) > 0


class TestGetPages:
    """GET /api/books/:id/pages"""

    def test_get_pages_after_generate(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )

        res = client.get(
            f"/api/books/{book_id}/pages",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        pages = res.json()
        assert len(pages) == 24

    def test_get_pages_empty_before_generate(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.get(
            f"/api/books/{book_id}/pages",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json() == []


class TestPageCountPerSpec:
    """판형별 페이지 수 범위 교차 검증"""

    def test_page_count_exceeds_130_rejected(self, client):
        """page_count 130 초과 값 거부 (SQUAREBOOK_HC)"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 132, "book_spec_uid": "SQUAREBOOK_HC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_a5_below_50_rejected(self, client):
        """PHOTOBOOK_A5_SC에 24p 설정 시 거부"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 24, "book_spec_uid": "PHOTOBOOK_A5_SC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_a5_50_accepted(self, client):
        """PHOTOBOOK_A5_SC에 50p 설정 허용"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 50, "book_spec_uid": "PHOTOBOOK_A5_SC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["page_count"] == 50

    def test_a5_200_accepted(self, client):
        """PHOTOBOOK_A5_SC에 200p 설정 허용"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 200, "book_spec_uid": "PHOTOBOOK_A5_SC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["page_count"] == 200

    def test_a5_above_200_rejected(self, client):
        """PHOTOBOOK_A5_SC에 202p 설정 시 거부"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 202, "book_spec_uid": "PHOTOBOOK_A5_SC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_squarebook_130_accepted(self, client):
        """SQUAREBOOK_HC에 130p 설정 허용"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"page_count": 130, "book_spec_uid": "SQUAREBOOK_HC"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["page_count"] == 130


class TestPlotInputValidation:
    """plot_input 길이 제한 검증"""

    def test_plot_input_over_1000_rejected(self, client):
        """1000자 초과 plot_input 거부"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        long_text = "가" * 1001
        res = client.patch(
            f"/api/books/{book_id}",
            json={"plot_input": long_text},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_plot_input_exactly_1000_accepted(self, client):
        """정확히 1000자 plot_input 허용"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        text_1000 = "가" * 1000
        res = client.patch(
            f"/api/books/{book_id}",
            json={"plot_input": text_1000},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert len(res.json()["plot_input"]) == 1000


class TestGenerateReCall:
    """generate 재호출 방어 검증"""

    def _setup_and_generate(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        # 첫 번째 생성
        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        return token, book_id

    def test_generate_twice_rejected(self, client):
        """이미 editing 상태인 책에 generate 재호출 시 422"""
        token, book_id = self._setup_and_generate(client)

        # 두 번째 생성 시도 → 거부
        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert "이미 생성된 동화책" in res.json()["detail"]

    def test_generate_completed_rejected(self, client):
        """completed 상태에서도 generate 거부"""
        token, book_id = self._setup_and_generate(client)

        # 상태를 completed로 변경
        client.patch(
            f"/api/books/{book_id}",
            json={"status": "completed"},
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        assert res.status_code == 422


class TestGeneratePageTypes:
    """생성된 페이지의 page_type 검증"""

    def test_page_types_title_content_ending(self, client):
        """title(1개) + content(N개) + ending(1개) 구성 확인"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "job_name": "소방관",
                "job_category": "안전/보안",
                "page_count": 24,
                "plot_input": "소방관 이야기",
            },
            headers=_auth_header(token),
        )

        res = client.post(
            f"/api/books/{book_id}/generate",
            headers=_auth_header(token),
        )
        data = res.json()
        pages = data["pages"]

        # 첫 페이지는 title
        assert pages[0]["page_type"] == "title"
        # 마지막 페이지는 ending
        assert pages[-1]["page_type"] == "ending"
        # 중간 페이지는 모두 content
        for page in pages[1:-1]:
            assert page["page_type"] == "content"
        # title 1개, ending 1개
        assert sum(1 for p in pages if p["page_type"] == "title") == 1
        assert sum(1 for p in pages if p["page_type"] == "ending") == 1
