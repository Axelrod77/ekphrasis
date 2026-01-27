"""Seed script to add Nifty 50 stocks to the database."""
import asyncio
import sys
sys.path.insert(0, "backend")
from app.database import async_session, engine
from app.models import Base
from app.models.stock import Stock
from sqlalchemy import select

NIFTY_50 = [
    ("RELIANCE", "Reliance Industries"), ("TCS", "Tata Consultancy Services"),
    ("HDFCBANK", "HDFC Bank"), ("INFY", "Infosys"), ("ICICIBANK", "ICICI Bank"),
    ("HINDUNILVR", "Hindustan Unilever"), ("ITC", "ITC"), ("SBIN", "State Bank of India"),
    ("BHARTIARTL", "Bharti Airtel"), ("KOTAKBANK", "Kotak Mahindra Bank"),
    ("LT", "Larsen & Toubro"), ("AXISBANK", "Axis Bank"), ("WIPRO", "Wipro"),
    ("ASIANPAINT", "Asian Paints"), ("MARUTI", "Maruti Suzuki"),
    ("TITAN", "Titan Company"), ("SUNPHARMA", "Sun Pharmaceutical"),
    ("ULTRACEMCO", "UltraTech Cement"), ("BAJFINANCE", "Bajaj Finance"),
    ("NESTLEIND", "Nestle India"), ("HCLTECH", "HCL Technologies"),
    ("TATAMOTORS", "Tata Motors"), ("NTPC", "NTPC"), ("POWERGRID", "Power Grid Corp"),
    ("M&M", "Mahindra & Mahindra"), ("ADANIENT", "Adani Enterprises"),
    ("ADANIPORTS", "Adani Ports"), ("ONGC", "Oil & Natural Gas Corp"),
    ("TATASTEEL", "Tata Steel"), ("JSWSTEEL", "JSW Steel"),
    ("COALINDIA", "Coal India"), ("BAJAJFINSV", "Bajaj Finserv"),
    ("TECHM", "Tech Mahindra"), ("HDFCLIFE", "HDFC Life Insurance"),
    ("SBILIFE", "SBI Life Insurance"), ("INDUSINDBK", "IndusInd Bank"),
    ("GRASIM", "Grasim Industries"), ("BRITANNIA", "Britannia Industries"),
    ("CIPLA", "Cipla"), ("APOLLOHOSP", "Apollo Hospitals"),
    ("DRREDDY", "Dr. Reddy's Laboratories"), ("EICHERMOT", "Eicher Motors"),
    ("DIVISLAB", "Divi's Laboratories"), ("BPCL", "Bharat Petroleum"),
    ("TATACONSUM", "Tata Consumer Products"), ("HEROMOTOCO", "Hero MotoCorp"),
    ("BAJAJ-AUTO", "Bajaj Auto"), ("HINDALCO", "Hindalco Industries"),
    ("UPL", "UPL"),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        for symbol, name in NIFTY_50:
            result = await db.execute(select(Stock).where(Stock.symbol == symbol))
            if not result.scalar_one_or_none():
                db.add(Stock(symbol=symbol, name=name))
        await db.commit()
    print(f"Seeded {len(NIFTY_50)} stocks")


if __name__ == "__main__":
    asyncio.run(seed())
