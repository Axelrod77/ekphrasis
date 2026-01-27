import random
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.stock import Stock, QuarterlyResult, AnnualResult, ShareholdingPattern


class ScreenerScraper:
    BASE_URL = "https://www.screener.in/company/{symbol}/consolidated/"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def scrape_stock(self, symbol: str) -> Stock:
        url = self.BASE_URL.format(symbol=symbol)
        ua = random.choice(settings.scraper_user_agents)
        headers = {"User-Agent": ua}

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                url = f"https://www.screener.in/company/{symbol}/"
                resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        data = self._parse_page(soup)

        result = await self.db.execute(select(Stock).where(Stock.symbol == symbol))
        stock = result.scalar_one_or_none()

        if stock:
            for key, value in data["ratios"].items():
                if hasattr(stock, key) and value is not None:
                    setattr(stock, key, value)
            stock.pros = data.get("pros")
            stock.cons = data.get("cons")
            stock.about = data.get("about")
            stock.last_scraped_at = datetime.utcnow()
        else:
            stock = Stock(
                symbol=symbol,
                name=data["ratios"].get("name", symbol),
                last_scraped_at=datetime.utcnow(),
                **{k: v for k, v in data["ratios"].items() if k != "name"},
            )
            self.db.add(stock)

        await self.db.flush()

        for q in data.get("quarterly", []):
            existing = await self.db.execute(
                select(QuarterlyResult)
                .where(QuarterlyResult.stock_id == stock.id, QuarterlyResult.quarter == q["quarter"])
            )
            if not existing.scalar_one_or_none():
                self.db.add(QuarterlyResult(stock_id=stock.id, **q))

        for a in data.get("annual", []):
            existing = await self.db.execute(
                select(AnnualResult)
                .where(AnnualResult.stock_id == stock.id, AnnualResult.fiscal_year == a["fiscal_year"])
            )
            if not existing.scalar_one_or_none():
                self.db.add(AnnualResult(stock_id=stock.id, **a))

        for s in data.get("shareholding", []):
            existing = await self.db.execute(
                select(ShareholdingPattern)
                .where(ShareholdingPattern.stock_id == stock.id, ShareholdingPattern.quarter == s["quarter"])
            )
            if not existing.scalar_one_or_none():
                self.db.add(ShareholdingPattern(stock_id=stock.id, **s))

        await self.db.commit()
        return stock

    def _parse_page(self, soup: BeautifulSoup) -> dict:
        data = {"ratios": {}, "quarterly": [], "annual": [], "shareholding": []}

        name_el = soup.select_one("h1")
        if name_el:
            data["ratios"]["name"] = name_el.get_text(strip=True)

        ratios_list = soup.select("#top-ratios li")
        ratio_map = {
            "Market Cap": "market_cap", "Current Price": "current_price",
            "Stock P/E": "pe_ratio", "Book Value": "book_value",
            "Dividend Yield": "dividend_yield", "ROCE": "roce",
            "ROE": "roe", "Face Value": "face_value",
        }
        for li in ratios_list:
            name_el = li.select_one(".name")
            val_el = li.select_one(".number")
            if not name_el or not val_el:
                continue
            name = name_el.get_text(strip=True).rstrip(" ₹%")
            val_text = val_el.get_text(strip=True).replace(",", "").replace("₹", "").strip()
            if name == "High / Low" and "/" in val_text:
                parts = val_text.split("/")
                try:
                    data["ratios"]["high_52w"] = float(parts[0].strip())
                    data["ratios"]["low_52w"] = float(parts[1].strip())
                except (ValueError, IndexError):
                    pass
                continue
            attr = ratio_map.get(name)
            if attr and val_text:
                try:
                    data["ratios"][attr] = float(val_text.replace("%", ""))
                except ValueError:
                    pass

        pros_section = soup.select_one(".pros")
        if pros_section:
            items = [li.get_text(strip=True) for li in pros_section.select("li")]
            data["pros"] = "\n".join(items) if items else None

        cons_section = soup.select_one(".cons")
        if cons_section:
            items = [li.get_text(strip=True) for li in cons_section.select("li")]
            data["cons"] = "\n".join(items) if items else None

        about_section = soup.select_one(".about p")
        if about_section:
            data["about"] = about_section.get_text(strip=True)

        quarters_section = soup.select_one("#quarters")
        if quarters_section:
            data["quarterly"] = self._parse_results_table(quarters_section, "quarter")

        pl_section = soup.select_one("#profit-loss")
        if pl_section:
            data["annual"] = self._parse_annual_table(pl_section)

        sh_section = soup.select_one("#shareholding")
        if sh_section:
            data["shareholding"] = self._parse_shareholding_table(sh_section)

        return data

    def _parse_results_table(self, section, period_key: str) -> list[dict]:
        table = section.select_one("table")
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        rows = table.select("tbody tr")
        field_map = {"Sales": "revenue", "Net Profit": "net_profit", "EPS": "eps", "OPM": "opm_percent"}
        row_data: dict[str, dict] = {}
        for row in rows:
            cells = row.select("td")
            if not cells:
                continue
            label = cells[0].get_text(strip=True)
            field = field_map.get(label)
            if not field:
                continue
            for i, cell in enumerate(cells[1:], 1):
                if i >= len(headers):
                    break
                period = headers[i]
                if period not in row_data:
                    row_data[period] = {period_key: period}
                val = cell.get_text(strip=True).replace(",", "").replace("%", "")
                try:
                    row_data[period][field] = float(val)
                except ValueError:
                    pass
        return list(row_data.values())

    def _parse_annual_table(self, section) -> list[dict]:
        table = section.select_one("table")
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        rows = table.select("tbody tr")
        field_map = {"Sales": "revenue", "Net Profit": "net_profit"}
        row_data: dict[str, dict] = {}
        for row in rows:
            cells = row.select("td")
            if not cells:
                continue
            label = cells[0].get_text(strip=True)
            field = field_map.get(label)
            if not field:
                continue
            for i, cell in enumerate(cells[1:], 1):
                if i >= len(headers):
                    break
                fy = headers[i]
                if fy not in row_data:
                    row_data[fy] = {"fiscal_year": fy}
                val = cell.get_text(strip=True).replace(",", "")
                try:
                    row_data[fy][field] = float(val)
                except ValueError:
                    pass
        return list(row_data.values())

    def _parse_shareholding_table(self, section) -> list[dict]:
        table = section.select_one("table")
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.select("thead th")]
        rows = table.select("tbody tr")
        field_map = {"Promoters": "promoter_percent", "FIIs": "fii_percent", "DIIs": "dii_percent", "Public": "public_percent"}
        row_data: dict[str, dict] = {}
        for row in rows:
            cells = row.select("td")
            if not cells:
                continue
            label = cells[0].get_text(strip=True)
            field = field_map.get(label)
            if not field:
                continue
            for i, cell in enumerate(cells[1:], 1):
                if i >= len(headers):
                    break
                q = headers[i]
                if q not in row_data:
                    row_data[q] = {"quarter": q}
                val = cell.get_text(strip=True).replace(",", "").replace("%", "")
                try:
                    row_data[q][field] = float(val)
                except ValueError:
                    pass
        return list(row_data.values())
