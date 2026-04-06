"""
태스크 2: 회원가입 / 로그인 / 인증 테스트
TDD RED 단계 — 모든 완료 기준을 테스트로 변환
"""
import pytest


# ============================================================
# 1. 회원가입 (POST /api/auth/signup)
# ============================================================

class TestSignup:
    """회원가입 API 테스트"""

    def test_signup_success(self, client):
        """정상 회원가입"""
        res = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_signup_duplicate_email(self, client):
        """이메일 중복 → 409"""
        client.post("/api/auth/signup", json={
            "email": "dup@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/signup", json={
            "email": "dup@example.com",
            "password": "password456",
            "name": "테스트",
            "phone": "01012345678",
        })
        assert res.status_code == 409
        assert "이미 가입된 이메일입니다" in res.json()["detail"]

    def test_signup_invalid_email(self, client):
        """유효하지 않은 이메일 → 422"""
        res = client.post("/api/auth/signup", json={
            "email": "not-an-email",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        assert res.status_code == 422
        assert "유효하지 않은 이메일 형식입니다" in res.json()["detail"]

    def test_signup_short_password(self, client):
        """비밀번호 8자 미만 → 422"""
        res = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "short",
            "name": "테스트",
            "phone": "01012345678",
        })
        assert res.status_code == 422
        assert "비밀번호는 8자 이상이어야 합니다" in res.json()["detail"]

    def test_signup_empty_email(self, client):
        """빈 이메일 → 422"""
        res = client.post("/api/auth/signup", json={
            "email": "",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        assert res.status_code == 422

    def test_signup_password_is_hashed(self, client, db_session):
        """비밀번호가 bcrypt로 해시 저장되는지 확인"""
        client.post("/api/auth/signup", json={
            "email": "hash@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        from app.models.user import User
        user = db_session.query(User).filter_by(email="hash@example.com").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.password_hash.startswith("$2")  # bcrypt prefix


# ============================================================
# 2. 로그인 (POST /api/auth/login)
# ============================================================

class TestLogin:
    """로그인 API 테스트"""

    def _create_user(self, client):
        client.post("/api/auth/signup", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })

    def test_login_success(self, client):
        """정상 로그인 → access_token + refresh_token (httpOnly 쿠키)"""
        self._create_user(client)
        res = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "password123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # httpOnly 쿠키에 refresh_token이 설정되었는지 확인
        cookies = res.cookies
        assert "refresh_token" in cookies

    def test_login_wrong_password(self, client):
        """비밀번호 오류 → 401"""
        self._create_user(client)
        res = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert "이메일 또는 비밀번호가 틀렸습니다" in res.json()["detail"]

    def test_login_nonexistent_email(self, client):
        """존재하지 않는 이메일 → 401"""
        res = client.post("/api/auth/login", json={
            "email": "noone@example.com",
            "password": "password123",
        })
        assert res.status_code == 401
        assert "이메일 또는 비밀번호가 틀렸습니다" in res.json()["detail"]


# ============================================================
# 3. 토큰 갱신 (POST /api/auth/refresh)
# ============================================================

class TestRefresh:
    """토큰 갱신 API 테스트"""

    def _login(self, client):
        """사용자 생성 + 로그인하여 쿠키 설정된 클라이언트 반환"""
        client.post("/api/auth/signup", json={
            "email": "refresh@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "refresh@example.com",
            "password": "password123",
        })
        return res

    def test_refresh_success(self, client):
        """정상 토큰 갱신 (httpOnly 쿠키에서 refresh token 읽기)"""
        login_res = self._login(client)
        # TestClient는 쿠키를 자동 관리하므로 refresh 호출 시 쿠키 포함
        res = client.post("/api/auth/refresh")
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_no_cookie(self, client):
        """쿠키 없이 refresh → 401"""
        # 로그인하지 않은 상태
        res = client.post("/api/auth/refresh")
        assert res.status_code == 401

    def test_refresh_access_token_type_rejected(self, client):
        """(a) access token을 refresh 쿠키에 넣으면 거부 → 401"""
        # 로그인으로 access token 획득
        client.post("/api/auth/signup", json={
            "email": "tokentype@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        login_res = client.post("/api/auth/login", json={
            "email": "tokentype@example.com",
            "password": "password123",
        })
        access_token = login_res.json()["access_token"]

        # 기존 쿠키 클리어 후 access token으로 설정
        client.cookies.clear()
        client.cookies.set("refresh_token", access_token)
        res = client.post("/api/auth/refresh")
        assert res.status_code == 401

    def test_refresh_deleted_user_rejected(self, client, db_session):
        """(b) 탈퇴한 사용자의 refresh token으로 갱신 시도 → 401"""
        self._login(client)

        # DB에서 사용자 직접 삭제 (탈퇴 시뮬레이션)
        from app.models.user import User
        user = db_session.query(User).filter_by(email="refresh@example.com").first()
        assert user is not None
        db_session.delete(user)
        db_session.commit()

        # 이미 설정된 쿠키로 refresh 시도 → 사용자 없으므로 거부
        res = client.post("/api/auth/refresh")
        assert res.status_code == 401


# ============================================================
# 4. 내 정보 조회 (GET /api/auth/me)
# ============================================================

class TestMe:
    """내 정보 조회 API 테스트"""

    def _login(self, client):
        client.post("/api/auth/signup", json={
            "email": "me@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        res = client.post("/api/auth/login", json={
            "email": "me@example.com",
            "password": "password123",
        })
        return res.json()["access_token"]

    def test_me_success(self, client):
        """정상 조회"""
        token = self._login(client)
        res = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "me@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_me_no_token(self, client):
        """토큰 없이 접근 → 401 또는 403"""
        res = client.get("/api/auth/me")
        assert res.status_code in (401, 403)

    def test_me_invalid_token(self, client):
        """잘못된 토큰 → 401"""
        res = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid-token",
        })
        assert res.status_code == 401

    def test_me_refresh_token_rejected(self, client):
        """(c) refresh token으로 /me 접근 시도 → 401 (access type만 허용)"""
        client.post("/api/auth/signup", json={
            "email": "reftok@example.com",
            "password": "password123",
            "name": "테스트",
            "phone": "01012345678",
        })
        login_res = client.post("/api/auth/login", json={
            "email": "reftok@example.com",
            "password": "password123",
        })
        refresh_token = login_res.json()["refresh_token"]

        # refresh token을 Authorization 헤더에 넣어서 /me 접근
        res = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {refresh_token}",
        })
        assert res.status_code == 401
