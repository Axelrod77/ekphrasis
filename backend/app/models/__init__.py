from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User
from app.models.stock import Stock, QuarterlyResult, AnnualResult, ShareholdingPattern, StockPeer, PriceHistory
from app.models.watchlist import Watchlist
from app.models.portfolio import Holding
from app.models.mutual_fund import MFScheme, UserMFHolding
from app.models.tax_harvest import TaxHarvestRecommendation
