"""캐릭터 API 테스트 — 태스크 7"""
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


class TestBookUpdateStyleFields:
    """PATCH /api/books/:id — story_style, art_style 필드 저장"""

    def test_update_story_style(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"story_style": "dreaming_today", "current_step": 3},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["story_style"] == "dreaming_today"

    def test_update_art_style(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"art_style": "watercolor", "current_step": 4},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["art_style"] == "watercolor"

    def test_update_invalid_story_style(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"story_style": "invalid_style"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_invalid_art_style(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"art_style": "invalid_style"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422


class TestCharacterCreate:
    """POST /api/books/:id/character"""

    def test_create_character(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["book_id"] == book_id
        assert data["generation_index"] == 0
        assert data["is_selected"] is False
        assert "image_path" in data

    def test_create_character_increments_generation_index(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 첫 번째 생성
        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        assert res1.json()["generation_index"] == 0

        # 두 번째 생성
        res2 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        assert res2.json()["generation_index"] == 1

    def test_create_character_max_regeneration(self, client):
        """최대 재생성 횟수 (초기 1회 + 재생성 4회 = 총 5회) 초과 시 422"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 5회 생성 (0, 1, 2, 3, 4)
        for i in range(5):
            res = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
            assert res.status_code == 201, f"Generation {i} failed"

        # 6번째 생성 시도 → 422
        res = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        assert res.status_code == 422
        assert "재생성 횟수를 모두 사용했습니다" in res.json()["detail"]

    def test_create_character_updates_regen_count(self, client):
        """캐릭터 생성 시 character_regen_count 증가"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 첫 번째 생성 — regen_count는 0 유지 (최초 생성은 카운트하지 않음)
        client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        book_res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert book_res.json()["character_regen_count"] == 0

        # 두 번째 생성 — regen_count 1
        client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        book_res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert book_res.json()["character_regen_count"] == 1

    def test_create_character_requires_auth(self, client):
        res = client.post("/api/books/1/character")
        assert res.status_code in (401, 403)

    def test_create_character_other_user_book(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_book(client, token1)

        res = client.post(
            f"/api/books/{book_id}/character",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_create_character_nonexistent_book(self, client):
        token = _signup_and_login(client)
        res = client.post(
            "/api/books/9999/character",
            headers=_auth_header(token),
        )
        assert res.status_code == 404


class TestCharacterGallery:
    """GET /api/books/:id/characters"""

    def test_get_empty_gallery(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.get(f"/api/books/{book_id}/characters", headers=_auth_header(token))
        assert res.status_code == 200
        assert res.json() == []

    def test_get_gallery_after_create(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))

        res = client.get(f"/api/books/{book_id}/characters", headers=_auth_header(token))
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        assert data[0]["generation_index"] == 0
        assert data[1]["generation_index"] == 1

    def test_get_gallery_requires_auth(self, client):
        res = client.get("/api/books/1/characters")
        assert res.status_code in (401, 403)

    def test_get_gallery_other_user_book(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_book(client, token1)

        res = client.get(
            f"/api/books/{book_id}/characters",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403


class TestCharacterSelect:
    """PATCH /api/books/:id/character/:charId/select"""

    def test_select_character(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 2개 생성
        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char1_id = res1.json()["id"]
        res2 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char2_id = res2.json()["id"]

        # 첫 번째 선택
        res = client.patch(
            f"/api/books/{book_id}/character/{char1_id}/select",
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["is_selected"] is True

        # 갤러리에서 확인 — 하나만 선택됨
        gallery = client.get(f"/api/books/{book_id}/characters", headers=_auth_header(token)).json()
        selected = [c for c in gallery if c["is_selected"]]
        assert len(selected) == 1
        assert selected[0]["id"] == char1_id

    def test_select_character_changes_selection(self, client):
        """다른 캐릭터 선택 시 이전 선택 해제"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char1_id = res1.json()["id"]
        res2 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char2_id = res2.json()["id"]

        # 첫 번째 선택
        client.patch(f"/api/books/{book_id}/character/{char1_id}/select", headers=_auth_header(token))

        # 두 번째로 변경
        client.patch(f"/api/books/{book_id}/character/{char2_id}/select", headers=_auth_header(token))

        gallery = client.get(f"/api/books/{book_id}/characters", headers=_auth_header(token)).json()
        selected = [c for c in gallery if c["is_selected"]]
        assert len(selected) == 1
        assert selected[0]["id"] == char2_id

    def test_select_character_nonexistent(self, client):
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}/character/9999/select",
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_select_character_wrong_book(self, client):
        """다른 책의 캐릭터 선택 시도"""
        token = _signup_and_login(client)
        book_id1 = _create_book(client, token)
        book_id2 = _create_book(client, token)

        res1 = client.post(f"/api/books/{book_id1}/character", headers=_auth_header(token))
        char_id = res1.json()["id"]

        # 다른 책에서 선택 시도
        res = client.patch(
            f"/api/books/{book_id2}/character/{char_id}/select",
            headers=_auth_header(token),
        )
        assert res.status_code == 404

    def test_select_character_requires_auth(self, client):
        res = client.patch("/api/books/1/character/1/select")
        assert res.status_code in (401, 403)

    def test_select_character_other_user(self, client):
        token1 = _signup_and_login(client, "user1@example.com")
        token2 = _signup_and_login(client, "user2@example.com")
        book_id = _create_book(client, token1)

        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token1))
        char_id = res1.json()["id"]

        res = client.patch(
            f"/api/books/{book_id}/character/{char_id}/select",
            headers=_auth_header(token2),
        )
        assert res.status_code == 403

    def test_select_character_updates_book_status(self, client):
        """캐릭터 선택 시 book.status가 character_confirmed로 변경되는지 확인"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # 캐릭터 생성 + 선택
        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char_id = res1.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=_auth_header(token))

        # book.status 확인
        book_res = client.get(f"/api/books/{book_id}", headers=_auth_header(token))
        assert book_res.json()["status"] == "character_confirmed"


class TestBookUpdateStatus:
    """PATCH /api/books/:id — status 필드 + step 전환 검증"""

    def test_update_status_valid(self, client):
        """유효한 status 값으로 업데이트"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"status": "character_confirmed"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["status"] == "character_confirmed"

    def test_update_status_invalid(self, client):
        """유효하지 않은 status 값 → 422"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"status": "invalid_status"},
            headers=_auth_header(token),
        )
        assert res.status_code == 422

    def test_update_story_and_art_style_together(self, client):
        """story_style + art_style 동시 업데이트"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        res = client.patch(
            f"/api/books/{book_id}",
            json={"story_style": "future_me", "art_style": "crayon"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        data = res.json()
        assert data["story_style"] == "future_me"
        assert data["art_style"] == "crayon"

    def test_step_5_to_6_without_character_selected(self, client):
        """캐릭터 미선택 상태에서 step 5→6 전환 시 422"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # step을 5로 설정
        client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 5},
            headers=_auth_header(token),
        )

        # 캐릭터 없이 step 6으로 전환 시도 → 422
        res = client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 6},
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert "캐릭터를 선택해주세요" in res.json()["detail"]

    def test_step_5_to_6_with_character_selected(self, client):
        """캐릭터 선택 후 step 5→6 전환 성공"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # step을 5로 설정
        client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 5},
            headers=_auth_header(token),
        )

        # 캐릭터 생성 + 선택
        res1 = client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))
        char_id = res1.json()["id"]
        client.patch(f"/api/books/{book_id}/character/{char_id}/select", headers=_auth_header(token))

        # step 6으로 전환 → 성공
        res = client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 6, "status": "character_confirmed"},
            headers=_auth_header(token),
        )
        assert res.status_code == 200
        assert res.json()["current_step"] == 6
        assert res.json()["status"] == "character_confirmed"

    def test_step_5_to_6_character_created_but_not_selected(self, client):
        """캐릭터 생성만 하고 선택 안 한 상태에서 step 6 전환 시 422"""
        token = _signup_and_login(client)
        book_id = _create_book(client, token)

        # step을 5로 설정
        client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 5},
            headers=_auth_header(token),
        )

        # 캐릭터 생성만 (선택 안 함)
        client.post(f"/api/books/{book_id}/character", headers=_auth_header(token))

        # step 6으로 전환 시도 → 422
        res = client.patch(
            f"/api/books/{book_id}",
            json={"current_step": 6},
            headers=_auth_header(token),
        )
        assert res.status_code == 422
        assert "캐릭터를 선택해주세요" in res.json()["detail"]
