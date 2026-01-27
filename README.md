# Ekphrasis

A full-stack Financial Analyst SaaS platform for Indian equity and mutual fund investors. Screen stocks with Screener.in-parity data, track portfolios at lot level, harvest tax losses, and analyze mutual fund performance against benchmarks.

## Features

### Stock Screener
- Filterable, sortable stock table with fundamental metrics (PE, PB, ROCE, ROE, D/E, dividend yield, promoter holding)
- Detailed stock pages with quarterly results, annual P&L, shareholding patterns, peer comparison, pros/cons
- Data scraped from Screener.in with rate limiting and User-Agent rotation
- Nightly Celery job refreshes top 500 stocks by market cap

### Portfolio Tracker
- Lot-level holdings with buy price, date, and quantity
- Real-time P&L calculation per holding and aggregate
- CSV import for bulk entry
- Visual P&L breakdown by stock (bar chart)

### Tax-Loss Harvesting
- Automatic analysis of all holdings for unrealized losses
- Per-lot short-term vs long-term classification (365-day threshold)
- Tax saving estimates using Budget 2024 rates (STCG 20%, LTCG 12.5%)
- Ranked recommendations sorted by tax saving potential
- Act/dismiss workflow for each recommendation
- Wash sale advisory notes

### Mutual Fund Analysis
- CAS PDF upload and parsing (CAMS & KFintech statements)
- Manual/CSV import of MF holdings
- Benchmark rating engine:
  - Weighted excess return score (0.2 × 1Y + 0.3 × 3Y + 0.5 × 5Y vs category average)
  - Good (>+2) / Average (-2 to +2) / Bad (<-2) classification
  - Expense ratio penalty (downgrade if > category median + 0.5%)
- Allocation breakdown by category (pie chart)
- Underperformer detection with top 3 alternative suggestions per category

### Auth
- JWT-based authentication with access + refresh tokens
- Protected routes on frontend, token auto-refresh via Axios interceptor

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic, Celery + Redis |
| Frontend | React 18, TypeScript, Vite, TanStack Query, Zustand, Tailwind CSS, Recharts |
| Database | PostgreSQL |
| Auth | JWT (python-jose + passlib[bcrypt]) |
| Scraping | httpx + BeautifulSoup |
| PDF Parsing | pdfplumber |
| Infrastructure | Docker Compose |

## Project Structure

```
ekphrasis/
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── alembic/
│   └── app/
│       ├── main.py              # FastAPI app + router registration
│       ├── config.py            # Pydantic settings
│       ├── database.py          # Async SQLAlchemy engine + session
│       ├── deps.py              # JWT auth dependency
│       ├── models/              # SQLAlchemy models
│       ├── schemas/             # Pydantic request/response schemas
│       ├── api/                 # Route handlers
│       │   ├── auth.py          # Register, login, refresh, me
│       │   ├── stocks.py        # List, detail, refresh
│       │   ├── watchlist.py     # CRUD with category filter
│       │   ├── portfolio.py     # Holdings CRUD, CSV import, summary
│       │   ├── mutual_funds.py  # CAS upload, import, holdings, analysis
│       │   └── tax_harvest.py   # Analyze, summary, recommendations
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── stock_service.py
│       │   ├── portfolio_service.py
│       │   ├── tax_harvest_engine.py
│       │   ├── cas_parser.py
│       │   ├── mf_analyzer.py
│       │   └── scraper/
│       │       ├── screener_scraper.py
│       │       └── cache.py
│       └── tasks/
│           ├── celery_app.py
│           └── scrape_stocks.py
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── pages/               # Login, Register, Dashboard, StockScreener,
│       │                        # StockDetail, Portfolio, MutualFunds, TaxHarvesting
│       ├── components/          # Layout, Navbar, StockCard, MetricsTable,
│       │                        # MFUploader, charts/
│       ├── hooks/               # useStocks, usePortfolio, useWatchlist,
│       │                        # useTaxHarvest, useMutualFunds
│       ├── store/authStore.ts
│       ├── api/client.ts
│       └── utils/format.ts
└── scripts/
    ├── seed_stocks.py           # Seed Nifty 50 stocks
    └── run_scraper.py           # Manual scraper runner
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development without Docker

### Run with Docker

```bash
git clone https://github.com/Axelrod77/ekphrasis.git
cd ekphrasis
docker-compose up
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on http://localhost:8000
- **Celery worker + beat** for background scraping
- **Frontend** on http://localhost:5173

### Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Start Postgres and Redis locally, then:
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Seed Data

```bash
cd backend
python ../scripts/seed_stocks.py        # Add Nifty 50 stocks to DB
python ../scripts/run_scraper.py RELIANCE  # Scrape a single stock
python ../scripts/run_scraper.py           # Scrape all seeded stocks
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get access + refresh tokens |
| POST | `/api/auth/refresh` | Refresh tokens |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/stocks` | List stocks (filter, sort, paginate) |
| GET | `/api/stocks/{symbol}` | Stock detail with quarterly, shareholding, peers |
| POST | `/api/stocks/{symbol}/refresh` | Re-scrape a stock |
| GET | `/api/watchlist` | User watchlist |
| POST | `/api/watchlist` | Add to watchlist |
| DELETE | `/api/watchlist/{id}` | Remove from watchlist |
| GET | `/api/portfolio/summary` | Portfolio with P&L |
| POST | `/api/portfolio/holdings` | Add holding |
| DELETE | `/api/portfolio/holdings/{id}` | Delete holding |
| POST | `/api/portfolio/import-csv` | Import holdings from CSV |
| POST | `/api/tax-harvest/analyze` | Run tax harvest analysis |
| GET | `/api/tax-harvest/summary` | Get current recommendations |
| PATCH | `/api/tax-harvest/recommendations/{id}` | Act on or dismiss |
| GET | `/api/mutual-funds/holdings` | MF holdings |
| POST | `/api/mutual-funds/upload-cas` | Upload CAS PDF |
| POST | `/api/mutual-funds/import` | Import MF holdings |
| GET | `/api/mutual-funds/analysis` | Ratings, allocation, suggestions |

## Configuration

Environment variables (set in `.env` or `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://ekphrasis:ekphrasis_dev@localhost:5432/ekphrasis` | Postgres connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | JWT signing key |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed origins |

## License

MIT
