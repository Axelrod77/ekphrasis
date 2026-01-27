import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, Integer, Text, DateTime, Date, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

stock_peers = Table(
    "stock_peers",
    Base.metadata,
    Column("stock_id", String(36), ForeignKey("stocks.id"), primary_key=True),
    Column("peer_stock_id", String(36), ForeignKey("stocks.id"), primary_key=True),
)

StockPeer = stock_peers


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    isin: Mapped[str | None] = mapped_column(String(12))
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100))
    market_cap: Mapped[float | None] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float)
    high_52w: Mapped[float | None] = mapped_column(Float)
    low_52w: Mapped[float | None] = mapped_column(Float)
    pe_ratio: Mapped[float | None] = mapped_column(Float)
    pb_ratio: Mapped[float | None] = mapped_column(Float)
    dividend_yield: Mapped[float | None] = mapped_column(Float)
    roce: Mapped[float | None] = mapped_column(Float)
    roe: Mapped[float | None] = mapped_column(Float)
    debt_to_equity: Mapped[float | None] = mapped_column(Float)
    eps: Mapped[float | None] = mapped_column(Float)
    book_value: Mapped[float | None] = mapped_column(Float)
    face_value: Mapped[float | None] = mapped_column(Float)
    promoter_holding: Mapped[float | None] = mapped_column(Float)
    sales_growth_3y: Mapped[float | None] = mapped_column(Float)
    profit_growth_3y: Mapped[float | None] = mapped_column(Float)
    pros: Mapped[str | None] = mapped_column(Text)
    cons: Mapped[str | None] = mapped_column(Text)
    about: Mapped[str | None] = mapped_column(Text)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quarterly_results = relationship("QuarterlyResult", back_populates="stock", cascade="all, delete-orphan")
    annual_results = relationship("AnnualResult", back_populates="stock", cascade="all, delete-orphan")
    shareholding_patterns = relationship("ShareholdingPattern", back_populates="stock", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")
    peers = relationship("Stock", secondary=stock_peers, primaryjoin=id == stock_peers.c.stock_id, secondaryjoin=id == stock_peers.c.peer_stock_id)


class QuarterlyResult(Base):
    __tablename__ = "quarterly_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks.id"), nullable=False)
    quarter: Mapped[str] = mapped_column(String(20), nullable=False)
    revenue: Mapped[float | None] = mapped_column(Float)
    net_profit: Mapped[float | None] = mapped_column(Float)
    eps: Mapped[float | None] = mapped_column(Float)
    opm_percent: Mapped[float | None] = mapped_column(Float)

    stock = relationship("Stock", back_populates="quarterly_results")


class AnnualResult(Base):
    __tablename__ = "annual_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks.id"), nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False)
    revenue: Mapped[float | None] = mapped_column(Float)
    net_profit: Mapped[float | None] = mapped_column(Float)
    roce: Mapped[float | None] = mapped_column(Float)
    roe: Mapped[float | None] = mapped_column(Float)
    debt_to_equity: Mapped[float | None] = mapped_column(Float)

    stock = relationship("Stock", back_populates="annual_results")


class ShareholdingPattern(Base):
    __tablename__ = "shareholding_patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks.id"), nullable=False)
    quarter: Mapped[str] = mapped_column(String(20), nullable=False)
    promoter_percent: Mapped[float | None] = mapped_column(Float)
    fii_percent: Mapped[float | None] = mapped_column(Float)
    dii_percent: Mapped[float | None] = mapped_column(Float)
    public_percent: Mapped[float | None] = mapped_column(Float)

    stock = relationship("Stock", back_populates="shareholding_patterns")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks.id"), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)

    stock = relationship("Stock", back_populates="price_history")
