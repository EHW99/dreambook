"""DB 모델 테스트 — 8개 테이블 생성 및 관계 검증"""
import pytest
from datetime import datetime, date
from sqlalchemy import inspect

from app.database import Base
from app.models import User, Photo, Book, CharacterSheet, Page, PageImage, Voucher, Order


class TestTableCreation:
    """8개 테이블이 정상적으로 생성되는지 검증"""

    def test_all_tables_exist(self, db_session):
        """8개 테이블이 모두 존재해야 한다"""
        inspector = inspect(db_session.bind)
        tables = inspector.get_table_names()
        expected = ["users", "photos", "books", "character_sheets",
                    "pages", "page_images", "vouchers", "orders"]
        for table in expected:
            assert table in tables, f"테이블 '{table}'이 존재하지 않음"

    def test_users_table_columns(self, db_session):
        """users 테이블의 컬럼 검증"""
        inspector = inspect(db_session.bind)
        columns = {col["name"] for col in inspector.get_columns("users")}
        expected = {"id", "email", "password_hash", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_books_table_columns(self, db_session):
        """books 테이블의 주요 컬럼 검증"""
        inspector = inspect(db_session.bind)
        columns = {col["name"] for col in inspector.get_columns("books")}
        expected = {"id", "user_id", "child_name", "job_name", "story_style",
                    "art_style", "page_count", "status", "current_step", "title",
                    "story_regen_count", "character_regen_count", "bookprint_book_uid"}
        assert expected.issubset(columns)

    def test_orders_table_columns(self, db_session):
        """orders 테이블의 주요 컬럼 검증"""
        inspector = inspect(db_session.bind)
        columns = {col["name"] for col in inspector.get_columns("orders")}
        expected = {"id", "user_id", "book_id", "bookprint_order_uid",
                    "status", "status_code", "recipient_name", "recipient_phone",
                    "postal_code", "address1", "total_amount"}
        assert expected.issubset(columns)


class TestUserModel:
    """User 모델 CRUD 테스트"""

    def test_create_user(self, db_session):
        user = User(email="test@example.com", password_hash="hashed_password")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.created_at is not None

    def test_email_unique_constraint(self, db_session):
        user1 = User(email="test@example.com", password_hash="hash1")
        db_session.add(user1)
        db_session.commit()

        user2 = User(email="test@example.com", password_hash="hash2")
        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()


class TestRelationships:
    """모델 간 관계 테스트"""

    def test_user_has_photos(self, db_session):
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        photo = Photo(
            user_id=user.id,
            file_path="/uploads/test.jpg",
            original_name="test.jpg",
            file_size=1024,
            width=800,
            height=600,
        )
        db_session.add(photo)
        db_session.commit()

        assert len(user.photos) == 1
        assert user.photos[0].original_name == "test.jpg"

    def test_book_has_pages_and_character_sheets(self, db_session):
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        book = Book(user_id=user.id, child_name="하늘이")
        db_session.add(book)
        db_session.commit()

        page = Page(book_id=book.id, page_number=1, page_type="title")
        cs = CharacterSheet(book_id=book.id, image_path="/img/char.png", generation_index=0)
        db_session.add_all([page, cs])
        db_session.commit()

        assert len(book.pages) == 1
        assert len(book.character_sheets) == 1

    def test_page_has_images(self, db_session):
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        book = Book(user_id=user.id, child_name="하늘이")
        db_session.add(book)
        db_session.commit()

        page = Page(book_id=book.id, page_number=1)
        db_session.add(page)
        db_session.commit()

        img = PageImage(page_id=page.id, image_path="/img/p1.png", generation_index=0)
        db_session.add(img)
        db_session.commit()

        assert len(page.images) == 1

    def test_cascade_delete_user(self, db_session):
        """사용자 삭제 시 관련 데이터 CASCADE 삭제"""
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        photo = Photo(user_id=user.id, file_path="/test.jpg",
                      original_name="test.jpg", file_size=1024, width=800, height=600)
        book = Book(user_id=user.id, child_name="하늘이")
        voucher = Voucher(user_id=user.id, voucher_type="story_only", price=9900)
        db_session.add_all([photo, book, voucher])
        db_session.commit()

        db_session.delete(user)
        db_session.commit()

        assert db_session.query(Photo).count() == 0
        assert db_session.query(Book).count() == 0
        assert db_session.query(Voucher).count() == 0


    def test_book_voucher_bidirectional_relationship(self, db_session):
        """Book ↔ Voucher 양방향 relationship 검증"""
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        voucher = Voucher(user_id=user.id, voucher_type="story_and_print", price=29900)
        db_session.add(voucher)
        db_session.commit()

        book = Book(user_id=user.id, child_name="하늘이", voucher_id=voucher.id)
        db_session.add(book)
        db_session.commit()

        # Book에서 Voucher 탐색 가능
        db_session.refresh(book)
        assert book.voucher is not None
        assert book.voucher.id == voucher.id
        assert book.voucher.voucher_type == "story_and_print"

        # Voucher에서 book_id 설정 후 Book 탐색 가능
        voucher.book_id = book.id
        db_session.commit()
        db_session.refresh(voucher)
        assert voucher.book is not None
        assert voucher.book.id == book.id
        assert voucher.book.child_name == "하늘이"

    def test_cascade_delete_user_deep(self, db_session):
        """User 삭제 시 Book → Pages → PageImages 중첩 CASCADE 삭제 검증"""
        user = User(email="test@example.com", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        book = Book(user_id=user.id, child_name="하늘이")
        db_session.add(book)
        db_session.commit()

        page = Page(book_id=book.id, page_number=1, page_type="content")
        db_session.add(page)
        db_session.commit()

        img = PageImage(page_id=page.id, image_path="/img/p1.png", generation_index=0)
        cs = CharacterSheet(book_id=book.id, image_path="/img/char.png", generation_index=0)
        db_session.add_all([img, cs])
        db_session.commit()

        # 삭제 전 확인
        assert db_session.query(Book).count() == 1
        assert db_session.query(Page).count() == 1
        assert db_session.query(PageImage).count() == 1
        assert db_session.query(CharacterSheet).count() == 1

        db_session.delete(user)
        db_session.commit()

        # 전부 삭제 확인
        assert db_session.query(Book).count() == 0
        assert db_session.query(Page).count() == 0
        assert db_session.query(PageImage).count() == 0
        assert db_session.query(CharacterSheet).count() == 0


class TestHealthEndpoint:
    """헬스체크 API 테스트"""

    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "dreambook-api"


class TestCORS:
    """CORS 설정 테스트"""

    def test_cors_headers(self, client):
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
