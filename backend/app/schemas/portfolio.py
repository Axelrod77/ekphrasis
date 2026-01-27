from pydantic import BaseModel
from datetime import date, datetime


class HoldingCreate(BaseModel):
    stock_id: str
    quantity: int
    buy_price: float
    buy_date: date


class HoldingResponse(BaseModel):
    id: str
    stock_id: str
    quantity: int
    buy_price: float
    buy_date: date
    created_at: datetime
    stock_symbol: str | None = None
    stock_name: str | None = None
    current_price: float | None = None
    current_value: float | None = None
    invested_value: float | None = None
    pnl: float | None = None
    pnl_percent: float | None = None

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_percent: float
    holdings: list[HoldingResponse]
