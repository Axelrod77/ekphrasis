from pydantic import BaseModel
from datetime import datetime
from app.schemas.stock import StockListItem


class WatchlistCreate(BaseModel):
    stock_id: str
    category: str = "bookmarked"


class WatchlistResponse(BaseModel):
    id: str
    stock_id: str
    category: str
    created_at: datetime
    stock: StockListItem

    model_config = {"from_attributes": True}
