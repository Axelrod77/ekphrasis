from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.mutual_fund import MFScheme, UserMFHolding
from app.schemas.mutual_fund import MFSchemeResponse, UserMFHoldingResponse, MFAnalysis
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/holdings", response_model=list[UserMFHoldingResponse])
async def get_mf_holdings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserMFHolding)
        .options(selectinload(UserMFHolding.scheme))
        .where(UserMFHolding.user_id == current_user.id)
    )
    holdings = result.scalars().all()

    return [
        UserMFHoldingResponse(
            id=h.id,
            scheme=MFSchemeResponse.model_validate(h.scheme),
            units=h.units,
            avg_nav=h.avg_nav,
            invested_amount=h.invested_amount,
            current_value=h.units * (h.scheme.nav or h.avg_nav) if h.scheme else None,
            pnl=(h.units * (h.scheme.nav or h.avg_nav) - h.invested_amount) if h.scheme else None,
            rating=h.scheme.computed_rating if h.scheme else None,
            source=h.source,
        )
        for h in holdings
    ]


@router.get("/analysis", response_model=MFAnalysis)
async def get_mf_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserMFHolding)
        .options(selectinload(UserMFHolding.scheme))
        .where(UserMFHolding.user_id == current_user.id)
    )
    holdings = result.scalars().all()

    total_invested = 0.0
    total_current_value = 0.0
    allocation_by_category: dict[str, float] = {}
    underperformers = []
    holding_responses = []

    for h in holdings:
        nav = h.scheme.nav or h.avg_nav if h.scheme else h.avg_nav
        current_val = h.units * nav
        total_invested += h.invested_amount
        total_current_value += current_val

        category = h.scheme.category if h.scheme else "Unknown"
        allocation_by_category[category] = allocation_by_category.get(category, 0) + current_val

        resp = UserMFHoldingResponse(
            id=h.id,
            scheme=MFSchemeResponse.model_validate(h.scheme) if h.scheme else None,
            units=h.units,
            avg_nav=h.avg_nav,
            invested_amount=h.invested_amount,
            current_value=current_val,
            pnl=current_val - h.invested_amount,
            rating=h.scheme.computed_rating if h.scheme else None,
            source=h.source,
        )
        holding_responses.append(resp)

        if h.scheme and h.scheme.return_1y and h.scheme.category_avg_1y:
            if h.scheme.return_1y < h.scheme.category_avg_1y:
                underperformers.append(resp)

    return MFAnalysis(
        holdings=holding_responses,
        total_invested=total_invested,
        total_current_value=total_current_value,
        allocation_by_category=allocation_by_category,
        underperformers=underperformers,
        suggestions=[],
    )


@router.post("/upload-cas")
async def upload_cas_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    return {"status": "ok", "message": "CAS parsing not yet implemented"}
