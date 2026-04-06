"""태스크 9: 편집/미리보기 — 텍스트 수정, 스토리 재생성, 이미지 재생성, 이미지 갤러리 테스트"""
import pytest


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


def _create_and_generate_book(client, token):
    """헬퍼: 동화책 생성 + 더미 스토리 생성까지 완료"""
    voucher_id = _purchase_voucher(client, token)
    res = client.post(
        "/api/books",
        json={"voucher_id": voucher_id},
        headers=_auth_header(token),
    )
    book_id = res.json()["id"]

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

    return book_id


class TestPatchPageText:
    """PATCH /api/books/:id/pages/:pageId — 텍스트 인라인 편집"""

    def test_update_page_text(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        # 페이지 목록 조회
        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        pages = res.json()
        page_id = pages[1]["id"]  # content 페이지

        # 텍스트 수정
        res = client.patch(
            f"/api/books/{book_id}/pages/{page_id}",
            json={"text_content": "수정된 텍스트입니다."},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["text_content"] == "수정된 텍스트입니다."

    def test_update_page_text_persists(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        client.patch(
            f"/api/books/{book_id}/pages/{page_id}",
            json={"text_content": "저장 확인용 텍스트"},
            headers=_auth_header(token),
        )

        # 다시 조회하여 저장 확인
        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        found = [p for p in res.json() if p["id"] == page_id]
        assert found[0]["text_content"] == "저장 확인용 텍스트"

    def test_update_page_text_other_user_forbidden(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_and_generate_book(client, token1)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token1))
        page_id = res.json()[0]["id"]

        res = client.patch(
            f"/api/books/{book_id}/pages/{page_id}",
            json={"text_content": "해킹 시도"},
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_update_nonexistent_page(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}/pages/99999",
            json={"text_content": "없는 페이지"},
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_update_page_empty_text_allowed(self, client):
        """빈 텍스트도 허용 (사용자가 지울 수 있어야 함)"""
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        res = client.patch(
            f"/api/books/{book_id}/pages/{page_id}",
            json={"text_content": ""},
            headers=_auth_header(token),
        )
        assert res.status_code == 200


class TestRegenerateStory:
    """POST /api/books/:id/regenerate-story — 스토리 재생성"""

    def test_regenerate_story_success(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert "pages" in data
        assert len(data["pages"]) > 0

    def test_regenerate_story_increments_count(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token),
        )

        res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.json()["story_regen_count"] == 1

    def test_regenerate_story_max_3_times(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        # 3회 재생성
        for _ in range(3):
            res = client.post(
                f"/api/books/{book_id}/regenerate-story",
                headers=_auth_header(token),
            )
            assert res.status_code == 200

        # 4회째 거부
        res = client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert "재생성 횟수" in res.json()["detail"]

    def test_regenerate_story_resets_image_regen_counts(self, client):
        """스토리 재생성 시 모든 페이지의 이미지 재생성 횟수가 리셋되어야 함"""
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        # 페이지 하나의 이미지를 재생성 (횟수 올리기)
        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]
        client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )

        # 스토리 재생성
        client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token),
        )

        # 모든 페이지의 이미지 재생성 횟수가 0이어야 함
        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        for page in res.json():
            assert page["image_regen_count"] == 0

    def test_regenerate_story_other_user_forbidden(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_and_generate_book(client, token1)

        res = client.post(
            f"/api/books/{book_id}/regenerate-story",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403


class TestRegenerateImage:
    """POST /api/books/:id/pages/:pageId/regenerate-image — 이미지 재생성"""

    def test_regenerate_image_success(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert "images" in data
        # 갤러리 방식: 기존 이미지 + 새 이미지
        assert len(data["images"]) == 2

    def test_regenerate_image_increments_count(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page = [p for p in res.json() if p["id"] == page_id][0]
        assert page["image_regen_count"] == 1

    def test_regenerate_image_max_4_times(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        for _ in range(4):
            res = client.post(
                f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
                headers=_auth_header(token),
            )
            assert res.status_code == 200

        # 5회째 거부
        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert "재생성 횟수" in res.json()["detail"]

    def test_regenerate_image_new_selected(self, client):
        """새 이미지가 자동으로 선택되어야 함"""
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        res = client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )
        data = res.json()
        selected_images = [img for img in data["images"] if img["is_selected"]]
        assert len(selected_images) == 1
        # 최신 이미지가 선택되어야 함
        assert selected_images[0]["generation_index"] == 1


class TestImageGallery:
    """GET /api/books/:id/pages/:pageId/images — 이미지 갤러리"""

    def test_get_images(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        res = client.get(
            f"/api/books/{book_id}/pages/{page_id}/images",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        images = res.json()
        assert len(images) >= 1

    def test_get_images_after_regenerate(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        # 이미지 재생성
        client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )

        res = client.get(
            f"/api/books/{book_id}/pages/{page_id}/images",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        images = res.json()
        assert len(images) == 2


class TestImageSelect:
    """PATCH /api/books/:id/pages/:pageId/images/:imgId/select — 이미지 선택"""

    def test_select_image(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        # 이미지 재생성하여 2개 만들기
        client.post(
            f"/api/books/{book_id}/pages/{page_id}/regenerate-image",
            headers=_auth_header(token),
        )

        # 이미지 목록 조회
        res = client.get(
            f"/api/books/{book_id}/pages/{page_id}/images",
            headers=_auth_header(token),
        )
        images = res.json()
        # 첫 번째(old) 이미지 선택
        old_image_id = images[0]["id"]

        res = client.patch(
            f"/api/books/{book_id}/pages/{page_id}/images/{old_image_id}/select",
            headers=_auth_header(token),
        )
        assert res.status_code == 200

        # 선택 확인
        res = client.get(
            f"/api/books/{book_id}/pages/{page_id}/images",
            headers=_auth_header(token),
        )
        images = res.json()
        selected = [img for img in images if img["is_selected"]]
        assert len(selected) == 1
        assert selected[0]["id"] == old_image_id

    def test_select_nonexistent_image(self, client):
        token = _signup_and_login(client)
        book_id = _create_and_generate_book(client, token)

        res = client.get(f"/api/books/{book_id}/pages", headers=_auth_header(token))
        page_id = res.json()[1]["id"]

        res = client.patch(
            f"/api/books/{book_id}/pages/{page_id}/images/99999/select",
            headers=_auth_header(token),
        )
        assert res.status_code == 404
