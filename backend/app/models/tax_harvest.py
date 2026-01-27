import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class TaxHarvestRecommendation(Base):
    __tablename__ = "tax_harvest_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    holding_id: Mapped[str] = mapped_column(String(36), ForeignKey("holdings.id"), nullable=False)
    unrealized_loss: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_tax_saving: Mapped[float] = mapped_column(Float, nullable=False)
    is_short_term: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tax_recommendations")
    holding = relationship("Holding", back_populates="tax_recommendations")
