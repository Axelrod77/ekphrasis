import asyncio
import time
from app.tasks.celery_app import celery
from app.database import async_session
from app.services.scraper.screener_scraper import ScreenerScraper
from app.models.stock import Stock
from sqlalchemy import select
from app.config import settings


@celery.task(name="app.tasks.scrape_stocks.refresh_top_stocks")
def refresh_top_stocks():
    asyncio.run(_refresh_top_stocks())


async def _refresh_top_stocks():
    async with async_session() as db:
        result = await db.execute(
            select(Stock.symbol)
            .where(Stock.market_cap.isnot(None))
            .order_by(Stock.market_cap.desc())
            .limit(500)
        )
        symbols = [row[0] for row in result.all()]

    for symbol in symbols:
        try:
            async with async_session() as db:
                scraper = ScreenerScraper(db)
                await scraper.scrape_stock(symbol)
            time.sleep(settings.scraper_rate_limit_seconds)
        except Exception as e:
            print(f"Error scraping {symbol}: {e}")


@celery.task(name="app.tasks.scrape_stocks.scrape_single_stock")
def scrape_single_stock(symbol: str):
    asyncio.run(_scrape_single(symbol))


async def _scrape_single(symbol: str):
    async with async_session() as db:
        scraper = ScreenerScraper(db)
        await scraper.scrape_stock(symbol)
