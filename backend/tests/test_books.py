"""동화책 API 테스트"""
import pytest


def _signup_and_login(client, email="test@example.com"):
    """헬퍼: 회원가입 + 로그인하여 토큰 반환"""
    client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "테스트", "phone": "01012345678"})
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _purchase_voucher(client, token, voucher_type="story_only"):
    """헬퍼: 이용권 구매"""
    res = client.post(
        "/api/vouchers/purchase",
        json={"voucher_type": voucher_type},
        headers=_auth_header(token),
    )
    return res.json()["id"]


class TestBookCreate:
    """POST /api/books"""

    def test_create_book_with_voucher(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "draft"
        assert data["current_step"] == 1
        assert data["voucher_id"] == voucher_id

    def test_create_book_voucher_gets_used(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        # 이용권이 used 상태로 변경되었는지 확인
        res = client.get("/api/vouchers", headers=_auth_header(token))
        vouchers = res.json()
        used = [v for v in vouchers if v["id"] == voucher_id]
        assert len(used) == 1
        assert used[0]["status"] == "used"

    def test_create_book_already_used_voucher(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        # 첫 번째 사용
        client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        # 두 번째 사용 시도
        res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        assert res.status_code == 400
        assert "이미 사용된" in res.json()["detail"]

    def test_create_book_nonexistent_voucher(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/books",
            json={"voucher_id": 9999},
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_create_book_other_user_voucher(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        voucher_id = _purchase_voucher(client, token1)
        # 다른 사용자의 이용권 사용 시도
        res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_create_book_requires_auth(self, client):
        res = client.post("/api/books", json={"voucher_id": 1})
        assert res.status_code in (401, 403)


class TestBookUpdate:
    """PATCH /api/books/:id"""

    def test_update_child_info(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}",
            json={
                "child_name": "홍길동",
                "child_birth_date": "2020-05-15",
                "current_step": 2,
            },
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["child_name"] == "홍길동"
        assert data["child_birth_date"] == "2020-05-15"
        assert data["current_step"] == 2

    def test_update_job_selection(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}",
            json={
                "job_category": "의료/과학",
                "job_name": "의사",
                "current_step": 3,
            },
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["job_category"] == "의료/과학"
        assert data["job_name"] == "의사"

    def test_update_child_name_too_long(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}",
            json={"child_name": "a" * 21},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_child_name_empty(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}",
            json={"child_name": "   "},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_nonexistent_book(self, client):
        token = _signup_and_login(client)
        res = client.patch(
            "/api/books/9999",
            json={"child_name": "홍길동"},
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_update_other_user_book(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        voucher_id = _purchase_voucher(client, token1)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token1),
        )
        book_id = book_res.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}",
            json={"child_name": "해킹"},
            headers=_auth_header(token2),
        )
        assert res.status_code == 403


class TestBookGet:
    """GET /api/books/:id"""

    def test_get_book(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.status_code == 200
        assert res.json()["id"] == book_id

    def test_get_nonexistent_book(self, client):
        token = _signup_and_login(client)
        res = client.get("/api/books/9999", headers=_auth_header(token))
        assert res.status_code == 404


class TestBookList:
    """GET /api/books"""

    def test_list_empty(self, client):
        token = _signup_and_login(client)
        res = client.get("/api/books", headers=_auth_header(token))
        assert res.status_code == 200
        assert res.json() == []

    def test_list_after_create(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        res = client.get("/api/books", headers=_auth_header(token))
        assert res.status_code == 200
        assert len(res.json()) == 1


class TestBookDelete:
    """DELETE /api/books/:id"""

    def test_delete_draft_book(self, client):
        token = _signup_and_login(client)
        voucher_id = _purchase_voucher(client, token)
        book_res = client.post(
            "/api/books",
            json={"voucher_id": voucher_id},
            headers=_auth_header(token),
        )
        book_id = book_res.json()["id"]

        res = client.delete(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.status_code == 200

        # 삭제 확인
        res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert res.status_code == 404
