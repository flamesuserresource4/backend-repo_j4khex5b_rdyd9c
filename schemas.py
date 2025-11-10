"""
Database Schemas for the SaaS Trading Platform

Each Pydantic model represents a collection in your MongoDB database.
Collection name = lowercase class name. Example: Strategy -> "strategy"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime

# Core user/account models
class ExchangeCredential(BaseModel):
    exchange: Literal[
        "alpaca",
        "binance",
        "binanceus",
        "bybit",
        "kraken",
        "oanda",
        "ibkr",
        "polygon",
        "tradier",
        "tda",
        "paper"
    ]
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    account_id: Optional[str] = None
    sandbox: bool = True
    label: Optional[str] = None

class User(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    plan: Literal["free", "pro", "enterprise"] = "free"
    organization: Optional[str] = None
    credentials: List[ExchangeCredential] = []
    is_active: bool = True

# Strategy and trading models
class Strategy(BaseModel):
    name: str = Field(..., description="Strategy name")
    description: Optional[str] = None
    asset_class: Literal["forex", "futures", "stocks", "options", "crypto"]
    symbols: List[str] = Field(..., description="List of tradable symbols")
    timeframe: Literal["1m", "5m", "15m", "1h", "4h", "1d"]
    mode: Literal["paper", "live"] = "paper"
    status: Literal["draft", "active", "paused"] = "draft"
    risk_per_trade_pct: float = Field(1.0, ge=0.1, le=5.0)
    max_concurrent_positions: int = Field(3, ge=1, le=20)
    code: Optional[str] = Field(None, description="Strategy code or reference to model repo")
    owner_email: Optional[EmailStr] = None

class Signal(BaseModel):
    strategy_id: str
    symbol: str
    side: Literal["buy", "sell"]
    confidence: float = Field(0.5, ge=0, le=1)
    price: Optional[float] = None
    quantity: Optional[float] = None
    metadata: Dict[str, Any] = {}
    generated_at: Optional[datetime] = None

class Trade(BaseModel):
    broker: str
    strategy_id: Optional[str] = None
    symbol: str
    side: Literal["buy", "sell"]
    qty: float
    price: Optional[float] = None
    status: Literal["submitted", "filled", "rejected", "canceled", "error"] = "submitted"
    order_id: Optional[str] = None
    error: Optional[str] = None

class WebhookEvent(BaseModel):
    broker: str
    payload: Dict[str, Any]

class BacktestRequest(BaseModel):
    strategy_code: str
    symbol: str
    timeframe: Literal["1m", "5m", "15m", "1h", "4h", "1d"]
    start: datetime
    end: datetime
    initial_capital: float = 10000.0

# Product catalog/pricing (for SaaS)
class Plan(BaseModel):
    name: Literal["free", "pro", "enterprise"]
    price_monthly: float
    features: List[str]
