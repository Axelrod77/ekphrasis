from pydantic import BaseModel
from datetime import datetime


class StockListItem(BaseModel):
    id: str
    symbol: str
    name: str
    sector: str | None = None
    market_cap: float | None = None
    current_price: float | None = None
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    roce: float | None = None
    roe: float | None = None
    dividend_yield: float | None = None
    promoter_holding: float | None = None

    model_config = {"from_attributes": True}


class QuarterlyResultSchema(BaseModel):
    quarter: str
    revenue: float | None = None
    net_profit: float | None = None
    eps: float | None = None
    opm_percent: float | None = None

    model_config = {"from_attributes": True}


class AnnualResultSchema(BaseModel):
    fiscal_year: str
    revenue: float | None = None
    net_profit: float | None = None
    roce: float | None = None
    roe: float | None = None
    debt_to_equity: float | None = None

    model_config = {"from_attributes": True}


class ShareholdingSchema(BaseModel):
    quarter: str
    promoter_percent: float | None = None
    fii_percent: float | None = None
    dii_percent: float | None = None
    public_percent: float | None = None

    model_config = {"from_attributes": True}


class StockDetail(StockListItem):
    isin: str | None = None
    industry: str | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    debt_to_equity: float | None = None
    eps: float | None = None
    book_value: float | None = None
    face_value: float | None = None
    sales_growth_3y: float | None = None
    profit_growth_3y: float | None = None
    pros: str | None = None
    cons: str | None = None
    about: str | None = None
    last_scraped_at: datetime | None = None
    quarterly_results: list[QuarterlyResultSchema] = []
    annual_results: list[AnnualResultSchema] = []
    shareholding_patterns: list[ShareholdingSchema] = []
    peers: list[StockListItem] = []


class StockListResponse(BaseModel):
    items: list[StockListItem]
    total: int
    page: int
    page_size: int
