from pydantic import BaseModel
from datetime import datetime


class MFSchemeResponse(BaseModel):
    id: str
    amfi_code: str
    scheme_name: str
    category: str | None = None
    fund_house: str | None = None
    nav: float | None = None
    expense_ratio: float | None = None
    return_1y: float | None = None
    return_3y: float | None = None
    return_5y: float | None = None
    computed_rating: str | None = None

    model_config = {"from_attributes": True}


class UserMFHoldingResponse(BaseModel):
    id: str
    scheme: MFSchemeResponse
    units: float
    avg_nav: float
    invested_amount: float
    current_value: float | None = None
    pnl: float | None = None
    rating: str | None = None
    source: str

    model_config = {"from_attributes": True}


class MFAnalysis(BaseModel):
    holdings: list[UserMFHoldingResponse]
    total_invested: float
    total_current_value: float
    allocation_by_category: dict[str, float]
    underperformers: list[UserMFHoldingResponse]
    suggestions: list[MFSchemeResponse]


class MFImportCreate(BaseModel):
    amfi_code: str
    units: float
    avg_nav: float
    invested_amount: float
