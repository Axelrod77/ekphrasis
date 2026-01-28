from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.watchlist import Watchlist
from app.models.stock import Stock
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.schemas.stock import StockListItem
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[WatchlistResponse])
async def get_watchlist(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Watchlist).options(selectinload(Watchlist.stock)).where(Watchlist.user_id == current_user.id)
    if category:
        query = query.where(Watchlist.category == category)

    result = await db.execute(query)
    items = result.scalars().all()

    return [
        WatchlistResponse(
            id=item.id,
            stock_id=item.stock_id,
            category=item.category,
            created_at=item.created_at,
            stock=StockListItem.model_validate(item.stock),
        )
        for item in items
    ]


@router.post("", response_model=WatchlistResponse)
async def add_to_watchlist(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock_result = await db.execute(select(Stock).where(Stock.id == data.stock_id))
    stock = stock_result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    existing = await db.execute(
        select(Watchlist).where(
            Watchlist.user_id == current_user.id,
            Watchlist.stock_id == data.stock_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    watchlist = Watchlist(
        user_id=current_user.id,
        stock_id=data.stock_id,
        category=data.category,
    )
    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)

    return WatchlistResponse(
        id=watchlist.id,
        stock_id=watchlist.stock_id,
        category=watchlist.category,
        created_at=watchlist.created_at,
        stock=StockListItem.model_validate(stock),
    )


@router.delete("/{id}")
async def remove_from_watchlist(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == id,
            Watchlist.user_id == current_user.id,
        )
    )
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    await db.delete(watchlist)
    await db.commit()
    return {"status": "ok"}
