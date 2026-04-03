"""태스크 3: 마이페이지 — 회원 정보 + 탈퇴 API 테스트"""
import pytest
from app.services.auth import hash_password


def _create_user(db_session, email="test@example.com", password="password123"):
    """테스트용 사용자 생성 헬퍼"""
    from app.models.user import User
    user = User(email=email, password_hash=hash_password(password))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _login(client, email="test@example.com", password="password123"):
    """로그인 후 access_token 반환"""
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ===== 비밀번호 변경 (PATCH /api/users/password) =====

class TestChangePassword:
    def test_change_password_success(self, client, db_session):
        """비밀번호 변경 성공"""
        _create_user(db_session)
        token = _login(client)
        res = client.patch(
            "/api/users/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["message"] == "비밀번호가 변경되었습니다"

        # 새 비밀번호로 로그인 가능
        res2 = client.post("/api/auth/login", json={"email": "test@example.com", "password": "newpassword123"})
        assert res2.status_code == 200

    def test_change_password_wrong_current(self, client, db_session):
        """현재 비밀번호가 틀린 경우 401"""
        _create_user(db_session)
        token = _login(client)
        res = client.patch(
            "/api/users/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
            headers=_auth_header(token),
        )
        assert res.status_code == 401
        assert res.json()["detail"] == "현재 비밀번호가 틀렸습니다"

    def test_change_password_too_short(self, client, db_session):
        """새 비밀번호가 8자 미만인 경우 422"""
        _create_user(db_session)
        token = _login(client)
        res = client.patch(
            "/api/users/password",
            json={
                "current_password": "password123",
                "new_password": "short",
            },
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert res.json()["detail"] == "새 비밀번호는 8자 이상이어야 합니다"

    def test_change_password_unauthorized(self, client):
        """인증 없이 비밀번호 변경 시 401/403"""
        res = client.patch(
            "/api/users/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
        )
        assert res.status_code == 403  # HTTPBearer returns 403 when no token

    def test_change_password_old_password_no_longer_works(self, client, db_session):
        """비밀번호 변경 후 이전 비밀번호로 로그인 불가"""
        _create_user(db_session)
        token = _login(client)
        client.patch(
            "/api/users/password",
            json={
                "current_password": "password123",
                "new_password": "newpassword123",
            },
            headers=_auth_header(token),
        )
        res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
        assert res.status_code == 401


# ===== 회원 탈퇴 (DELETE /api/users/me) =====

class TestDeleteAccount:
    def test_delete_account_success(self, client, db_session):
        """회원 탈퇴 성공"""
        _create_user(db_session)
        token = _login(client)
        res = client.delete("/api/users/me", headers=_auth_header(token))
        assert res.status_code == 200
        assert res.json()["message"] == "회원 탈퇴가 완료되었습니다"

    def test_delete_account_cascade_db(self, client, db_session):
        """회원 탈퇴 시 관련 DB 레코드 모두 삭제"""
        from app.models.user import User
        from app.models.photo import Photo

        user = _create_user(db_session)
        # 사진 레코드 추가
        photo = Photo(
            user_id=user.id,
            file_path="/uploads/test.jpg",
            original_name="test.jpg",
            file_size=1024,
            width=1024,
            height=1024,
        )
        db_session.add(photo)
        db_session.commit()

        token = _login(client)
        res = client.delete("/api/users/me", headers=_auth_header(token))
        assert res.status_code == 200

        # 사용자 삭제 확인
        assert db_session.query(User).filter(User.id == user.id).first() is None
        # 사진 레코드 삭제 확인
        assert db_session.query(Photo).filter(Photo.user_id == user.id).first() is None

    def test_delete_account_unauthorized(self, client):
        """인증 없이 탈퇴 시 401/403"""
        res = client.delete("/api/users/me")
        assert res.status_code == 403

    def test_delete_account_cannot_login_after(self, client, db_session):
        """탈퇴 후 로그인 불가"""
        _create_user(db_session)
        token = _login(client)
        client.delete("/api/users/me", headers=_auth_header(token))

        res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
        assert res.status_code == 401

    def test_delete_account_photo_files_deleted(self, client, db_session, tmp_path):
        """회원 탈퇴 시 사진 파일도 삭제"""
        from app.models.photo import Photo
        import os

        user = _create_user(db_session)

        # 임시 파일 생성
        photo_file = tmp_path / "test_photo.jpg"
        photo_file.write_bytes(b"fake image data")
        assert photo_file.exists()

        photo = Photo(
            user_id=user.id,
            file_path=str(photo_file),
            original_name="test_photo.jpg",
            file_size=1024,
            width=1024,
            height=1024,
        )
        db_session.add(photo)
        db_session.commit()

        token = _login(client)
        res = client.delete("/api/users/me", headers=_auth_header(token))
        assert res.status_code == 200

        # 파일 삭제 확인
        assert not photo_file.exists()
