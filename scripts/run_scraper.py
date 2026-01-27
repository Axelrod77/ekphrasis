"""Run scraper for a single stock or all seeded stocks."""
import asyncio
import sys
import time
sys.path.insert(0, "backend")
from app.database import async_session
from app.services.scraper.screener_scraper import ScreenerScraper
from app.models.stock import Stock
from app.config import settings
from sqlalchemy import select


async def scrape_one(symbol: str):
    async with async_session() as db:
        scraper = ScreenerScraper(db)
        stock = await scraper.scrape_stock(symbol)
        print(f"Scraped {stock.symbol}: price={stock.current_price}, PE={stock.pe_ratio}")


async def scrape_all():
    async with async_session() as db:
        result = await db.execute(select(Stock.symbol))
        symbols = [r[0] for r in result.all()]

    for sym in symbols:
        try:
            await scrape_one(sym)
            time.sleep(settings.scraper_rate_limit_seconds)
        except Exception as e:
            print(f"Error: {sym}: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(scrape_one(sys.argv[1]))
    else:
        asyncio.run(scrape_all())
