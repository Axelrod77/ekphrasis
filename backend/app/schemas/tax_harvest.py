from pydantic import BaseModel
from datetime import datetime


class TaxHarvestRecommendationResponse(BaseModel):
    id: str
    holding_id: str
    stock_symbol: str | None = None
    stock_name: str | None = None
    quantity: int | None = None
    buy_price: float | None = None
    current_price: float | None = None
    unrealized_loss: float
    estimated_tax_saving: float
    is_short_term: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TaxHarvestSummary(BaseModel):
    total_unrealized_loss: float
    total_estimated_tax_saving: float
    stcg_harvestable: float
    ltcg_harvestable: float
    recommendations: list[TaxHarvestRecommendationResponse]


class TaxHarvestAction(BaseModel):
    status: str
