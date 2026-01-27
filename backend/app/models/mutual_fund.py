import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class MFScheme(Base):
    __tablename__ = "mf_schemes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    amfi_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(500), nullable=False)
    isin: Mapped[str | None] = mapped_column(String(12))
    category: Mapped[str | None] = mapped_column(String(100))
    sub_category: Mapped[str | None] = mapped_column(String(100))
    fund_house: Mapped[str | None] = mapped_column(String(200))
    nav: Mapped[float | None] = mapped_column(Float)
    expense_ratio: Mapped[float | None] = mapped_column(Float)
    return_1y: Mapped[float | None] = mapped_column(Float)
    return_3y: Mapped[float | None] = mapped_column(Float)
    return_5y: Mapped[float | None] = mapped_column(Float)
    category_avg_1y: Mapped[float | None] = mapped_column(Float)
    category_avg_3y: Mapped[float | None] = mapped_column(Float)
    category_avg_5y: Mapped[float | None] = mapped_column(Float)
    category_median_expense: Mapped[float | None] = mapped_column(Float)
    computed_rating: Mapped[str | None] = mapped_column(String(20))
    last_updated: Mapped[datetime | None] = mapped_column(DateTime)

    user_holdings = relationship("UserMFHolding", back_populates="scheme", cascade="all, delete-orphan")


class UserMFHolding(Base):
    __tablename__ = "user_mf_holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    scheme_id: Mapped[str] = mapped_column(String(36), ForeignKey("mf_schemes.id"), nullable=False)
    units: Mapped[float] = mapped_column(Float, nullable=False)
    avg_nav: Mapped[float] = mapped_column(Float, nullable=False)
    invested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(20), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mf_holdings")
    scheme = relationship("MFScheme", back_populates="user_holdings")
