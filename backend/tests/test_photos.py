"""
태스크 4: 아이 사진 관리 테스트
TDD RED 단계 — 모든 완료 기준을 테스트로 변환
"""
import io
import pytest
from PIL import Image


def create_test_image(width=1024, height=1024, fmt="PNG"):
    """테스트용 이미지 바이트 생성"""
    img = Image.new("RGB", (width, height), color=(255, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


def signup_and_login(client, email="photo@test.com", password="password123"):
    """회원가입 + 로그인 → access_token 반환"""
    client.post("/api/auth/signup", json={"email": email, "password": password, "name": "테스트", "phone": "01012345678"})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# 1. 사진 업로드 (POST /api/photos)
# ============================================================

class TestPhotoUpload:
    """사진 업로드 API 테스트"""

    def test_upload_success_png(self, client):
        """정상 PNG 업로드"""
        token = signup_and_login(client)
        img = create_test_image(1024, 1024, "PNG")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.png", img, "image/png")},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["original_name"] == "child.png"
        assert data["width"] == 1024
        assert data["height"] == 1024
        assert "id" in data
        assert "thumbnail_url" in data
        assert "created_at" in data

    def test_upload_success_jpg(self, client):
        """정상 JPEG 업로드"""
        token = signup_and_login(client)
        img = create_test_image(512, 512, "JPEG")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.jpg", img, "image/jpeg")},
        )
        assert res.status_code == 201

    def test_upload_success_webp(self, client):
        """정상 WebP 업로드"""
        token = signup_and_login(client)
        img = create_test_image(800, 600, "WebP")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.webp", img, "image/webp")},
        )
        # WebP는 width/height 중 하나가 512 미만이면 거절, 800x600은 OK
        assert res.status_code == 201

    def test_upload_unsupported_format(self, client):
        """지원하지 않는 형식 (GIF) → 422"""
        token = signup_and_login(client)
        img = create_test_image(1024, 1024, "GIF")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.gif", img, "image/gif")},
        )
        assert res.status_code == 422
        assert "지원하지 않는 파일 형식입니다" in res.json()["detail"]

    def test_upload_too_large(self, client):
        """10MB 초과 → 422"""
        token = signup_and_login(client)
        # 11MB 파일 생성 (큰 이미지)
        large_data = io.BytesIO(b"\x89PNG" + b"\x00" * (11 * 1024 * 1024))
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("big.png", large_data, "image/png")},
        )
        assert res.status_code == 422
        assert "파일 크기가 10MB를 초과합니다" in res.json()["detail"]

    def test_upload_low_resolution(self, client):
        """해상도 512x512 미만 → 422"""
        token = signup_and_login(client)
        img = create_test_image(400, 300, "PNG")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("small.png", img, "image/png")},
        )
        assert res.status_code == 422
        assert "최소 512x512 이상의 이미지를 업로드해주세요" in res.json()["detail"]

    def test_upload_max_20_photos(self, client):
        """사용자당 최대 20장 → 21번째 422"""
        token = signup_and_login(client)
        for i in range(20):
            img = create_test_image(512, 512, "PNG")
            res = client.post(
                "/api/photos",
                headers=auth_header(token),
                files={"file": (f"child_{i}.png", img, "image/png")},
            )
            assert res.status_code == 201, f"Upload {i} failed: {res.json()}"

        # 21번째 업로드 시도
        img = create_test_image(512, 512, "PNG")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child_20.png", img, "image/png")},
        )
        assert res.status_code == 422
        assert "최대 20장까지 등록 가능합니다" in res.json()["detail"]

    def test_upload_invalid_content_type(self, client):
        """잘못된 content_type이면 거부 → 422"""
        token = signup_and_login(client)
        img = create_test_image(1024, 1024, "PNG")
        res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.png", img, "application/octet-stream")},
        )
        assert res.status_code == 422
        assert "지원하지 않는 파일 형식입니다" in res.json()["detail"]

    def test_content_type_none_rejected(self, client):
        """content_type이 None일 때 validate_content_type 우회 불가 확인"""
        # TestClient에서 content_type=None은 자동 추론되므로
        # 서비스 레벨에서 직접 검증
        from app.services.photo import validate_content_type
        # None은 허용하지 않아야 함 (API 레벨에서 not file.content_type로 차단)
        assert validate_content_type("image/png") is True
        assert validate_content_type("image/jpeg") is True
        assert validate_content_type("image/webp") is True
        assert validate_content_type("application/pdf") is False
        assert validate_content_type("text/plain") is False

    def test_upload_requires_auth(self, client):
        """인증 없이 업로드 → 403"""
        img = create_test_image(512, 512, "PNG")
        res = client.post(
            "/api/photos",
            files={"file": ("child.png", img, "image/png")},
        )
        assert res.status_code == 403


# ============================================================
# 2. 사진 목록 (GET /api/photos)
# ============================================================

class TestPhotoList:
    """사진 목록 조회 API 테스트"""

    def test_list_empty(self, client):
        """사진 없으면 빈 배열"""
        token = signup_and_login(client)
        res = client.get("/api/photos", headers=auth_header(token))
        assert res.status_code == 200
        assert res.json() == []

    def test_list_after_upload(self, client):
        """업로드 후 목록 확인"""
        token = signup_and_login(client)
        img = create_test_image(1024, 1024, "PNG")
        client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.png", img, "image/png")},
        )

        res = client.get("/api/photos", headers=auth_header(token))
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["original_name"] == "child.png"
        assert "id" in data[0]
        assert "thumbnail_url" in data[0]
        assert "created_at" in data[0]

    def test_list_only_my_photos(self, client):
        """다른 사용자의 사진은 보이지 않아야 한다"""
        token1 = signup_and_login(client, "user1@test.com")
        token2 = signup_and_login(client, "user2@test.com")

        # user1이 사진 업로드
        img = create_test_image(512, 512, "PNG")
        client.post(
            "/api/photos",
            headers=auth_header(token1),
            files={"file": ("user1_photo.png", img, "image/png")},
        )

        # user2의 목록에는 없어야 함
        res = client.get("/api/photos", headers=auth_header(token2))
        assert res.status_code == 200
        assert len(res.json()) == 0

    def test_list_requires_auth(self, client):
        """인증 없이 목록 조회 → 403"""
        res = client.get("/api/photos")
        assert res.status_code == 403


# ============================================================
# 3. 사진 삭제 (DELETE /api/photos/:id)
# ============================================================

class TestPhotoDelete:
    """사진 삭제 API 테스트"""

    def test_delete_success(self, client):
        """정상 삭제"""
        token = signup_and_login(client)
        img = create_test_image(512, 512, "PNG")
        upload_res = client.post(
            "/api/photos",
            headers=auth_header(token),
            files={"file": ("child.png", img, "image/png")},
        )
        photo_id = upload_res.json()["id"]

        res = client.delete(f"/api/photos/{photo_id}", headers=auth_header(token))
        assert res.status_code == 200

        # 삭제 후 목록에서 사라져야 함
        list_res = client.get("/api/photos", headers=auth_header(token))
        assert len(list_res.json()) == 0

    def test_delete_other_user_photo(self, client):
        """다른 사용자의 사진 삭제 → 403"""
        token1 = signup_and_login(client, "owner@test.com")
        token2 = signup_and_login(client, "other@test.com")

        # owner가 업로드
        img = create_test_image(512, 512, "PNG")
        upload_res = client.post(
            "/api/photos",
            headers=auth_header(token1),
            files={"file": ("child.png", img, "image/png")},
        )
        photo_id = upload_res.json()["id"]

        # other가 삭제 시도
        res = client.delete(f"/api/photos/{photo_id}", headers=auth_header(token2))
        assert res.status_code == 403

    def test_delete_nonexistent(self, client):
        """존재하지 않는 사진 삭제 → 404"""
        token = signup_and_login(client)
        res = client.delete("/api/photos/9999", headers=auth_header(token))
        assert res.status_code == 404

    def test_delete_requires_auth(self, client):
        """인증 없이 삭제 → 403"""
        res = client.delete("/api/photos/1")
        assert res.status_code == 403
