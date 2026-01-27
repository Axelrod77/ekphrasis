import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock")
    tax_recommendations = relationship("TaxHarvestRecommendation", back_populates="holding", cascade="all, delete-orphan")
