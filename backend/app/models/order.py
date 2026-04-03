from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    bookprint_order_uid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PAID")
    status_code: Mapped[int] = mapped_column(Integer, default=20)
    recipient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    address1: Mapped[str] = mapped_column(String(200), nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    shipping_memo: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    total_amount: Mapped[int] = mapped_column(Integer, default=0)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tracking_carrier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ordered_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="orders")
    book = relationship("Book", back_populates="order")
