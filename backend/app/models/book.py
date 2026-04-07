from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    voucher_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vouchers.id"), nullable=True)
    child_name: Mapped[str] = mapped_column(String(50), nullable=False)
    child_gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    child_birth_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    photo_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("photos.id"), nullable=True)
    job_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    job_outfit: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    story_style: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    art_style: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=24)
    book_spec_uid: Mapped[str] = mapped_column(String(50), default="SQUAREBOOK_HC")
    plot_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    story_regen_count: Mapped[int] = mapped_column(Integer, default=0)
    character_regen_count: Mapped[int] = mapped_column(Integer, default=0)
    cover_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bookprint_book_uid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    thumbnail_dir: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="books")
    voucher = relationship("Voucher", foreign_keys=[voucher_id], uselist=False)
    character_sheets = relationship("CharacterSheet", back_populates="book", cascade="all, delete-orphan")
    pages = relationship("Page", back_populates="book", cascade="all, delete-orphan")
    order = relationship("Order", back_populates="book", uselist=False, cascade="all, delete-orphan")
