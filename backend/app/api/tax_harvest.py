from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.tax_harvest import TaxHarvestRecommendation
from app.models.portfolio import Holding
from app.schemas.tax_harvest import TaxHarvestRecommendationResponse, TaxHarvestSummary, TaxHarvestAction
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()

STCG_TAX_RATE = 0.15
LTCG_TAX_RATE = 0.10


@router.get("/summary", response_model=TaxHarvestSummary)
async def get_tax_harvest_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TaxHarvestRecommendation)
        .options(selectinload(TaxHarvestRecommendation.holding).selectinload(Holding.stock))
        .where(TaxHarvestRecommendation.user_id == current_user.id)
    )
    recommendations = result.scalars().all()

    total_unrealized_loss = 0.0
    total_estimated_tax_saving = 0.0
    stcg_harvestable = 0.0
    ltcg_harvestable = 0.0
    rec_responses = []

    for rec in recommendations:
        total_unrealized_loss += rec.unrealized_loss
        total_estimated_tax_saving += rec.estimated_tax_saving

        if rec.is_short_term:
            stcg_harvestable += rec.unrealized_loss
        else:
            ltcg_harvestable += rec.unrealized_loss

        holding = rec.holding
        stock = holding.stock if holding else None

        rec_responses.append(TaxHarvestRecommendationResponse(
            id=rec.id,
            holding_id=rec.holding_id,
            stock_symbol=stock.symbol if stock else None,
            stock_name=stock.name if stock else None,
            quantity=holding.quantity if holding else None,
            buy_price=holding.buy_price if holding else None,
            current_price=stock.current_price if stock else None,
            unrealized_loss=rec.unrealized_loss,
            estimated_tax_saving=rec.estimated_tax_saving,
            is_short_term=rec.is_short_term,
            status=rec.status,
            created_at=rec.created_at,
        ))

    return TaxHarvestSummary(
        total_unrealized_loss=total_unrealized_loss,
        total_estimated_tax_saving=total_estimated_tax_saving,
        stcg_harvestable=stcg_harvestable,
        ltcg_harvestable=ltcg_harvestable,
        recommendations=rec_responses,
    )


@router.post("/analyze")
async def analyze_tax_harvest(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Holding)
        .options(selectinload(Holding.stock))
        .where(Holding.user_id == current_user.id)
    )
    holdings = result.scalars().all()

    today = date.today()
    one_year_ago = today - timedelta(days=365)

    await db.execute(
        select(TaxHarvestRecommendation)
        .where(TaxHarvestRecommendation.user_id == current_user.id)
    )

    created_count = 0
    for holding in holdings:
        if not holding.stock or not holding.stock.current_price:
            continue

        current_value = holding.quantity * holding.stock.current_price
        invested_value = holding.quantity * holding.buy_price
        pnl = current_value - invested_value

        if pnl >= 0:
            continue

        unrealized_loss = abs(pnl)
        is_short_term = holding.buy_date > one_year_ago
        tax_rate = STCG_TAX_RATE if is_short_term else LTCG_TAX_RATE
        estimated_tax_saving = unrealized_loss * tax_rate

        existing = await db.execute(
            select(TaxHarvestRecommendation).where(
                TaxHarvestRecommendation.user_id == current_user.id,
                TaxHarvestRecommendation.holding_id == holding.id,
                TaxHarvestRecommendation.status == "pending",
            )
        )
        if existing.scalar_one_or_none():
            continue

        rec = TaxHarvestRecommendation(
            user_id=current_user.id,
            holding_id=holding.id,
            unrealized_loss=unrealized_loss,
            estimated_tax_saving=estimated_tax_saving,
            is_short_term=is_short_term,
        )
        db.add(rec)
        created_count += 1

    await db.commit()
    return {"status": "ok", "recommendations_created": created_count}


@router.patch("/recommendations/{id}")
async def update_recommendation(
    id: str,
    data: TaxHarvestAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TaxHarvestRecommendation).where(
            TaxHarvestRecommendation.id == id,
            TaxHarvestRecommendation.user_id == current_user.id,
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = data.status
    await db.commit()
    return {"status": "ok"}
