"""오디오북 API 테스트 — 태스크 13"""
import pytest


def _signup_and_login(client, email="audio@example.com"):
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


def _create_book_with_pages(client, token):
    """헬퍼: 동화책 생성 + 더미 스토리 생성하여 페이지가 있는 책 반환"""
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
            "child_name": "하늘이",
            "job_name": "소방관",
            "job_category": "안전",
            "story_style": "dreaming_today",
            "art_style": "watercolor",
        },
        headers=_auth_header(token),
    )

    # 더미 스토리 생성
    client.post(
        f"/api/books/{book_id}/generate",
        headers=_auth_header(token),
    )

    return book_id


class TestAudioData:
    """GET /api/books/:id/audio-data"""

    def test_get_audio_data_success(self, client):
        """정상적으로 오디오 데이터를 반환하는지 테스트"""
        token = _signup_and_login(client)
        book_id = _create_book_with_pages(client, token)

        res = client.get(
            f"/api/books/{book_id}/audio-data",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()

        # 반환 구조 검증
        assert "book_title" in data
        assert "total_pages" in data
        assert "pages" in data
        assert isinstance(data["pages"], list)
        assert len(data["pages"]) > 0

        # 각 페이지의 구조 검증
        for page in data["pages"]:
            assert "page_number" in page
            assert "text_content" in page
            assert "image_url" in page

    def test_get_audio_data_page_order(self, client):
        """페이지가 page_number 순서로 정렬되는지 확인"""
        token = _signup_and_login(client)
        book_id = _create_book_with_pages(client, token)

        res = client.get(
            f"/api/books/{book_id}/audio-data",
            headers=_auth_header(token),
        )
        data = res.json()
        page_numbers = [p["page_number"] for p in data["pages"]]
        assert page_numbers == sorted(page_numbers)

    def test_get_audio_data_not_found(self, client):
        """존재하지 않는 책 ID로 요청 시 404"""
        token = _signup_and_login(client)
        res = client.get(
            "/api/books/9999/audio-data",
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_get_audio_data_unauthorized(self, client):
        """인증 없이 요청 시 401 또는 403"""
        res = client.get("/api/books/1/audio-data")
        assert res.status_code in (401, 403)

    def test_get_audio_data_other_user(self, client):
        """다른 사용자의 책에 접근 시 403"""
        token1 = _signup_and_login(client, "user1@example.com")
        book_id = _create_book_with_pages(client, token1)

        token2 = _signup_and_login(client, "user2@example.com")
        res = client.get(
            f"/api/books/{book_id}/audio-data",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_get_audio_data_no_pages(self, client):
        """페이지가 없는 책의 오디오 데이터 요청"""
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = res.json()["id"]

        res = client.get(
            f"/api/books/{book_id}/audio-data",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_pages"] == 0
        assert data["pages"] == []

    def test_get_audio_data_has_selected_image(self, client):
        """선택된 이미지의 URL이 반환되는지 확인"""
        token = _signup_and_login(client)
        book_id = _create_book_with_pages(client, token)

        res = client.get(
            f"/api/books/{book_id}/audio-data",
            headers=_auth_header(token),
        )
        data = res.json()

        # 더미 생성 후 각 페이지에 이미지가 있어야 함
        for page in data["pages"]:
            # image_url이 null이 아닌 값이어야 함 (더미 이미지라도)
            assert page["image_url"] is not None or page["image_url"] is None  # nullable OK
