from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.portfolio import Holding
from app.models.stock import Stock
from app.schemas.portfolio import HoldingCreate, HoldingResponse, PortfolioSummary
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Holding).options(selectinload(Holding.stock)).where(Holding.user_id == current_user.id)
    )
    holdings = result.scalars().all()

    total_invested = 0.0
    current_value = 0.0
    holding_responses = []

    for h in holdings:
        invested = h.quantity * h.buy_price
        current = h.quantity * (h.stock.current_price or h.buy_price) if h.stock else invested
        pnl = current - invested
        pnl_percent = (pnl / invested * 100) if invested else 0

        total_invested += invested
        current_value += current

        holding_responses.append(HoldingResponse(
            id=h.id,
            stock_id=h.stock_id,
            quantity=h.quantity,
            buy_price=h.buy_price,
            buy_date=h.buy_date,
            created_at=h.created_at,
            stock_symbol=h.stock.symbol if h.stock else None,
            stock_name=h.stock.name if h.stock else None,
            current_price=h.stock.current_price if h.stock else None,
            current_value=current,
            invested_value=invested,
            pnl=pnl,
            pnl_percent=pnl_percent,
        ))

    total_pnl = current_value - total_invested
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested else 0

    return PortfolioSummary(
        total_invested=total_invested,
        current_value=current_value,
        total_pnl=total_pnl,
        total_pnl_percent=total_pnl_percent,
        holdings=holding_responses,
    )


@router.post("/holdings", response_model=HoldingResponse)
async def add_holding(
    data: HoldingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock_result = await db.execute(select(Stock).where(Stock.id == data.stock_id))
    stock = stock_result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    holding = Holding(
        user_id=current_user.id,
        stock_id=data.stock_id,
        quantity=data.quantity,
        buy_price=data.buy_price,
        buy_date=data.buy_date,
    )
    db.add(holding)
    await db.commit()
    await db.refresh(holding)

    invested = holding.quantity * holding.buy_price
    current = holding.quantity * (stock.current_price or holding.buy_price)
    pnl = current - invested

    return HoldingResponse(
        id=holding.id,
        stock_id=holding.stock_id,
        quantity=holding.quantity,
        buy_price=holding.buy_price,
        buy_date=holding.buy_date,
        created_at=holding.created_at,
        stock_symbol=stock.symbol,
        stock_name=stock.name,
        current_price=stock.current_price,
        current_value=current,
        invested_value=invested,
        pnl=pnl,
        pnl_percent=(pnl / invested * 100) if invested else 0,
    )


@router.delete("/holdings/{id}")
async def delete_holding(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Holding).where(
            Holding.id == id,
            Holding.user_id == current_user.id,
        )
    )
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    await db.delete(holding)
    await db.commit()
    return {"status": "ok"}
