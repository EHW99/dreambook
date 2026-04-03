"""이용권 API 테스트"""
import pytest


def _signup_and_login(client):
    """헬퍼: 회원가입 + 로그인하여 토큰 반환"""
    client.post("/api/auth/signup", json={"email": "test@example.com", "password": "password123"})
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    return res.json()["access_token"]


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


class TestVoucherPurchase:
    """POST /api/vouchers/purchase"""

    def test_purchase_story_only(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "story_only"},
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["voucher_type"] == "story_only"
        assert data["price"] == 9900
        assert data["status"] == "purchased"

    def test_purchase_story_and_print(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "story_and_print"},
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["voucher_type"] == "story_and_print"
        assert data["price"] == 29900
        assert data["status"] == "purchased"

    def test_purchase_invalid_type(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "invalid"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_purchase_requires_auth(self, client):
        res = client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "story_only"},
        )
        assert res.status_code in (401, 403)


class TestVoucherList:
    """GET /api/vouchers"""

    def test_list_empty(self, client):
        token = _signup_and_login(client)
        res = client.get("/api/vouchers", headers=_auth_header(token))
        assert res.status_code == 200
        assert res.json() == []

    def test_list_after_purchase(self, client):
        token = _signup_and_login(client)
        client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "story_only"},
            headers=_auth_header(token),
        )
        client.post(
            "/api/vouchers/purchase",
            json={"voucher_type": "story_and_print"},
            headers=_auth_header(token),
        )
        res = client.get("/api/vouchers", headers=_auth_header(token))
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2

    def test_list_requires_auth(self, client):
        res = client.get("/api/vouchers")
        assert res.status_code in (401, 403)
