from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)  # card, bank_transfer, kakao_pay
    status: Mapped[str] = mapped_column(String(20), default="completed")  # completed, refunded
    merchant_uid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 주문번호
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    vouchers = relationship("Voucher", back_populates="payment")
