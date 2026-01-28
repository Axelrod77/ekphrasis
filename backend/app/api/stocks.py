from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockListItem, StockDetail, StockListResponse
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=StockListResponse)
async def list_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    sector: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    min_pe: float | None = None,
    max_pe: float | None = None,
    min_roce: float | None = None,
    min_roe: float | None = None,
    min_market_cap: float | None = None,
    max_debt_to_equity: float | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Stock)

    if search:
        query = query.where(or_(
            Stock.symbol.ilike(f"%{search}%"),
            Stock.name.ilike(f"%{search}%"),
        ))
    if sector:
        query = query.where(Stock.sector == sector)
    if min_pe is not None:
        query = query.where(Stock.pe_ratio >= min_pe)
    if max_pe is not None:
        query = query.where(Stock.pe_ratio <= max_pe)
    if min_roce is not None:
        query = query.where(Stock.roce >= min_roce)
    if min_roe is not None:
        query = query.where(Stock.roe >= min_roe)
    if min_market_cap is not None:
        query = query.where(Stock.market_cap >= min_market_cap)
    if max_debt_to_equity is not None:
        query = query.where(Stock.debt_to_equity <= max_debt_to_equity)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    if sort_by:
        sort_col = getattr(Stock, sort_by, Stock.market_cap)
        query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
    else:
        query = query.order_by(Stock.market_cap.desc().nullslast())

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    stocks = result.scalars().all()

    return StockListResponse(
        items=[StockListItem.model_validate(s) for s in stocks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{symbol}", response_model=StockDetail)
async def get_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Stock).where(Stock.symbol == symbol.upper()))
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return StockDetail(
        id=stock.id,
        symbol=stock.symbol,
        name=stock.name,
        sector=stock.sector,
        market_cap=stock.market_cap,
        current_price=stock.current_price,
        pe_ratio=stock.pe_ratio,
        pb_ratio=stock.pb_ratio,
        roce=stock.roce,
        roe=stock.roe,
        dividend_yield=stock.dividend_yield,
        promoter_holding=stock.promoter_holding,
        isin=stock.isin,
        industry=stock.industry,
        high_52w=stock.high_52w,
        low_52w=stock.low_52w,
        debt_to_equity=stock.debt_to_equity,
        eps=stock.eps,
        book_value=stock.book_value,
        face_value=stock.face_value,
        sales_growth_3y=stock.sales_growth_3y,
        profit_growth_3y=stock.profit_growth_3y,
        pros=stock.pros,
        cons=stock.cons,
        about=stock.about,
        last_scraped_at=stock.last_scraped_at,
        quarterly_results=[],
        annual_results=[],
        shareholding_patterns=[],
        peers=[],
    )
