import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.stock import Stock
from app.schemas.stock import StockListItem, StockDetail, StockListResponse
from app.deps import get_current_user
from app.models.user import User
from app.services.scraper.screener_scraper import ScreenerScraper

logger = logging.getLogger(__name__)

router = APIRouter()


async def _scrape_stock(symbol: str, db: AsyncSession) -> Stock:
    scraper = ScreenerScraper(db)
    stock = await scraper.scrape_stock(symbol.upper())
    return stock


async def _load_stock_detail(symbol: str, db: AsyncSession) -> Stock | None:
    result = await db.execute(
        select(Stock)
        .where(Stock.symbol == symbol.upper())
        .options(
            selectinload(Stock.quarterly_results),
            selectinload(Stock.annual_results),
            selectinload(Stock.shareholding_patterns),
            selectinload(Stock.peers),
        )
    )
    return result.scalar_one_or_none()


def _stock_to_detail(stock: Stock) -> StockDetail:
    return StockDetail.model_validate(stock)


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
    stock = await _load_stock_detail(symbol, db)

    if not stock:
        # Auto-scrape from screener.in
        try:
            await _scrape_stock(symbol, db)
        except Exception:
            logger.exception("Failed to scrape stock %s", symbol)
            raise HTTPException(status_code=404, detail="Stock not found")
        stock = await _load_stock_detail(symbol, db)

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return _stock_to_detail(stock)


@router.post("/scrape/{symbol}", response_model=StockDetail)
async def scrape_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await _scrape_stock(symbol, db)
    except Exception:
        logger.exception("Failed to scrape stock %s", symbol)
        raise HTTPException(status_code=404, detail=f"Could not scrape stock '{symbol}' from screener.in")

    stock = await _load_stock_detail(symbol, db)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found after scraping")

    return _stock_to_detail(stock)


@router.post("/search-scrape", response_model=StockListResponse)
async def search_scrape(
    term: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attempt to scrape the search term as a symbol if not found in DB."""
    try:
        await _scrape_stock(term, db)
    except Exception:
        logger.exception("Failed to scrape stock %s", term)
        raise HTTPException(status_code=404, detail=f"Could not find or scrape '{term}'")

    result = await db.execute(
        select(Stock).where(Stock.symbol == term.upper())
    )
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Could not find '{term}' after scraping")

    return StockListResponse(
        items=[StockListItem.model_validate(stock)],
        total=1,
        page=1,
        page_size=20,
    )
