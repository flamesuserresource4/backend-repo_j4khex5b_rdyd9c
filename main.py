import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import db, create_document, get_documents
from schemas import User, Strategy, Signal, Trade, WebhookEvent, BacktestRequest, Plan

app = FastAPI(title="AI Hedge SaaS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Hedge SaaS Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                cols = db.list_collection_names()
                response["collections"] = cols[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# SaaS: public plans
@app.get("/plans", response_model=List[Plan])
def get_plans():
    plans = [
        Plan(name="free", price_monthly=0, features=["1 strategy", "Paper trading", "Community support"]),
        Plan(name="pro", price_monthly=49, features=["Unlimited strategies", "Live trading", "Priority support", "Webhooks"]),
        Plan(name="enterprise", price_monthly=299, features=["SLA", "Dedicated infra", "Custom integrations"]) ,
    ]
    return plans

# Users CRUD (minimal)
@app.post("/users")
def create_user(user: User):
    user_id = create_document("user", user)
    return {"id": user_id}

@app.get("/users")
def list_users():
    return get_documents("user", {}, 50)

# Strategy CRUD (minimal)
@app.post("/strategies")
def create_strategy(strategy: Strategy):
    strategy_id = create_document("strategy", strategy)
    return {"id": strategy_id}

@app.get("/strategies")
def list_strategies():
    return get_documents("strategy", {}, 100)

# Signals ingestion
@app.post("/signals")
def ingest_signal(signal: Signal):
    signal.generated_at = signal.generated_at or datetime.utcnow()
    sid = create_document("signal", signal)
    return {"id": sid}

# Trades log
@app.post("/trades")
def log_trade(trade: Trade):
    tid = create_document("trade", trade)
    return {"id": tid}

# Generic webhook to integrate with external providers (e.g., TradingView alerts)
@app.post("/webhook")
def webhook(event: WebhookEvent):
    wid = create_document("webhookevent", event)
    return {"id": wid}

# Simple backtest stub (store request and return echo for now)
class BacktestResult(BaseModel):
    total_return_pct: float
    sharpe: float
    max_drawdown_pct: float
    trades: int

@app.post("/backtest", response_model=BacktestResult)
def backtest(req: BacktestRequest):
    create_document("backtestrequest", req)
    # Placeholder metrics (in real integration we would call ai-hedge-fund backtester)
    return BacktestResult(
        total_return_pct=12.4,
        sharpe=1.1,
        max_drawdown_pct=6.2,
        trades=42,
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
