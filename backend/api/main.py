"""
FastAPI Application

HK-focused automated trading simulation platform.
Supports IBKR, FUTU, CCXT, and YFinance data sources.
"""

import logging
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..config import (
    API_CONFIG,
    HK_DEFAULT_SYMBOLS,
    CCXT_CONFIG,
    SIMULATION_CONFIG,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="biu.1 AI Quant — HK Trading Simulation Platform",
        version="0.2.0",
        description=(
            "Fully automated trading strategy simulation platform targeting "
            "HK markets (IBKR, FUTU) and crypto (CCXT) with YFinance data."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=API_CONFIG.get("cors_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

system_coordinator = None
_simulation_engine = None
_active_broker_name: str = "paper"   # paper | ibkr | futu | ccxt

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class SystemStartRequest(BaseModel):
    symbols: Optional[List[str]] = None
    data_source: str = "yfinance"   # yfinance | ccxt
    broker: str = "paper"           # paper | ibkr | futu | ccxt
    timeframe: str = "1d"


class BacktestRequest(BaseModel):
    symbols: Optional[List[str]] = None
    data_source: str = "yfinance"
    period: str = "1y"
    interval: str = "1d"
    strategy: str = "macd"          # macd | rsi | macd_rsi


class BrokerConfigRequest(BaseModel):
    broker: str                      # paper | ibkr | futu | ccxt
    paper_trading: bool = True


# ---------------------------------------------------------------------------
# Helper: build simulation engine
# ---------------------------------------------------------------------------

def _build_engine(symbols: List[str], data_source: str, broker_name: str):
    from ..simulation.engine import SimulationEngine
    from ..brokers.ibkr_broker import IBKRBroker
    from ..brokers.futu_broker import FUTUBroker
    from ..brokers.ccxt_broker import CCXTBroker
    from ..brokers.paper_broker import PaperBroker

    broker_map = {
        "paper": PaperBroker,
        "ibkr": IBKRBroker,
        "futu": FUTUBroker,
        "ccxt": CCXTBroker,
    }
    broker_cls = broker_map.get(broker_name, PaperBroker)
    broker = broker_cls() if broker_name != "paper" else PaperBroker(
        initial_capital=SIMULATION_CONFIG["initial_capital"]
    )
    broker.connect()

    engine = SimulationEngine(
        symbols=symbols,
        data_source=data_source,
        initial_capital=SIMULATION_CONFIG["initial_capital"],
    )
    engine.broker = broker
    return engine


def _get_strategy_fn(strategy_name: str):
    """Return a strategy function by name."""
    from ..utils.indicators import calculate_macd, calculate_rsi

    def macd_strategy(engine, symbol, data):
        if len(data) < 30:
            return None
        prices = data["Close"].values
        _, _, histogram = calculate_macd(prices)
        if len(histogram) < 2:
            return None
        if histogram[-2] < 0 and histogram[-1] > 0:
            return "buy"
        if histogram[-2] > 0 and histogram[-1] < 0:
            return "sell"
        return None

    def rsi_strategy(engine, symbol, data):
        if len(data) < 15:
            return None
        prices = data["Close"].values
        rsi = calculate_rsi(prices)
        if rsi[-1] < 30:
            return "buy"
        if rsi[-1] > 70:
            return "sell"
        return None

    def macd_rsi_strategy(engine, symbol, data):
        m = macd_strategy(engine, symbol, data)
        r = rsi_strategy(engine, symbol, data)
        if m == r:
            return m
        return None

    strategies = {
        "macd": macd_strategy,
        "rsi": rsi_strategy,
        "macd_rsi": macd_rsi_strategy,
    }
    return strategies.get(strategy_name, macd_strategy)


# ---------------------------------------------------------------------------
# System Control
# ---------------------------------------------------------------------------

@app.post("/api/system/start")
async def start_system(req: SystemStartRequest):
    global system_coordinator, _simulation_engine, _active_broker_name

    _active_broker_name = req.broker
    symbols = req.symbols or HK_DEFAULT_SYMBOLS

    if system_coordinator is None:
        from ..agents.coordinator import AgentCoordinator
        from ..agents.data_agent import DataAgent
        from ..agents.macd_agent import MACDStrategyAgent
        from ..agents.decision_agent import DecisionAgent
        from ..agents.execution_agent import ExecutionAgent
        from ..agents.risk_agent import RiskManagementAgent
        from ..brokers.paper_broker import PaperBroker

        broker = PaperBroker(initial_capital=SIMULATION_CONFIG["initial_capital"])
        broker.connect()

        system_coordinator = AgentCoordinator()
        data_agent = DataAgent("data_agent", symbols=symbols, timeframe=req.timeframe)
        macd_agent = MACDStrategyAgent("macd_agent")
        decision_agent = DecisionAgent("decision_agent")
        execution_agent = ExecutionAgent("execution_agent", broker=broker)
        risk_agent = RiskManagementAgent("risk_agent")

        system_coordinator.register_agent("data_agent", data_agent)
        system_coordinator.register_agent("macd_agent", macd_agent)
        system_coordinator.register_agent("decision_agent", decision_agent)
        system_coordinator.register_agent("execution_agent", execution_agent)
        system_coordinator.register_agent("risk_agent", risk_agent)
        system_coordinator.start()

    # Also initialise simulation engine
    _simulation_engine = _build_engine(symbols, req.data_source, req.broker)

    return {"status": "running", "broker": req.broker, "symbols": symbols}


@app.post("/api/system/stop")
async def stop_system():
    global system_coordinator, _simulation_engine
    if system_coordinator is not None:
        system_coordinator.stop()
        system_coordinator = None
    if _simulation_engine is not None:
        _simulation_engine.stop()
        _simulation_engine = None
    return {"status": "stopped"}


@app.get("/api/system/status")
async def get_system_status():
    global system_coordinator, _simulation_engine, _active_broker_name
    if system_coordinator is None:
        return {"status": "stopped", "agents": [], "broker": _active_broker_name}

    agents = [
        {"name": name, "status": "running" if agent.running else "stopped"}
        for name, agent in system_coordinator.agents.items()
    ]
    sim_status = _simulation_engine.get_status() if _simulation_engine else {}
    return {
        "status": "running",
        "broker": _active_broker_name,
        "agents": agents,
        "simulation": sim_status,
    }


# ---------------------------------------------------------------------------
# Market Data
# ---------------------------------------------------------------------------

@app.get("/api/market/symbols")
async def get_hk_symbols():
    """Return the default HK symbol list."""
    return {"market": "HKEX", "symbols": HK_DEFAULT_SYMBOLS}


@app.get("/api/market/crypto-symbols")
async def get_crypto_symbols():
    """Return the default crypto symbol list."""
    return {"exchange": CCXT_CONFIG["default_exchange"],
            "symbols": CCXT_CONFIG["default_symbols"]}


@app.get("/api/market/price/{symbol}")
async def get_price(symbol: str):
    """Fetch the latest price for a symbol."""
    from ..data.yfinance_source import YFinanceSource
    src = YFinanceSource()
    price = src.get_latest_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail=f"No price found for {symbol}")
    return {"symbol": symbol, "price": price}


@app.get("/api/market/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, period: str = "3mo", interval: str = "1d"):
    """Return OHLCV data for charting."""
    from ..data.yfinance_source import YFinanceSource
    src = YFinanceSource()
    df = src.fetch(symbol, period=period, interval=interval)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    records = df.reset_index()
    # Normalise the date/datetime index column name regardless of yfinance version
    date_col = next((c for c in records.columns if c.lower() in ("date", "datetime", "index")), None)
    if date_col and date_col != "date":
        records = records.rename(columns={date_col: "date"})
    records["date"] = records["date"].astype(str)
    return {"symbol": symbol, "data": records.to_dict(orient="records")}


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

@app.post("/api/backtest/run")
async def run_backtest(req: BacktestRequest):
    """Run a strategy backtest over historical data."""
    symbols = req.symbols or HK_DEFAULT_SYMBOLS
    engine = _build_engine(symbols, req.data_source, "paper")
    strategy_fn = _get_strategy_fn(req.strategy)
    engine.set_strategy(strategy_fn)
    try:
        results = engine.run_backtest(period=req.period, interval=req.interval)
        return results
    except Exception as exc:
        logger.error("Backtest error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Broker Config
# ---------------------------------------------------------------------------

@app.get("/api/broker/list")
async def list_brokers():
    """Return available broker adapters and their connection status."""
    from ..brokers.ibkr_broker import IBKRBroker
    from ..brokers.futu_broker import FUTUBroker
    from ..brokers.ccxt_broker import CCXTBroker
    from ..config import IBKR_CONFIG, FUTU_CONFIG, CCXT_BROKER_CONFIG

    return {
        "brokers": [
            {"name": "paper",  "enabled": True,  "paper_trading": True,  "description": "Built-in simulation"},
            {"name": "ibkr",   "enabled": IBKR_CONFIG.get("enabled", False),  "paper_trading": IBKR_CONFIG.get("paper_trading", True),  "description": "Interactive Brokers (TWS)"},
            {"name": "futu",   "enabled": FUTU_CONFIG.get("enabled", False),  "paper_trading": FUTU_CONFIG.get("paper_trading", True),  "description": "Futu OpenD"},
            {"name": "ccxt",   "enabled": CCXT_BROKER_CONFIG.get("enabled", False), "paper_trading": CCXT_BROKER_CONFIG.get("sandbox", True), "description": f"CCXT ({CCXT_BROKER_CONFIG.get('exchange', 'binance')})"},
        ]
    }


# ---------------------------------------------------------------------------
# Trades & Portfolio
# ---------------------------------------------------------------------------

@app.get("/api/trades")
async def get_trades():
    global system_coordinator
    if system_coordinator is None:
        return []
    execution_agent = system_coordinator.agents.get("execution_agent")
    if execution_agent is None:
        return []
    return execution_agent.orders


@app.get("/api/portfolio")
async def get_portfolio():
    global system_coordinator
    if system_coordinator is None:
        return {}
    execution_agent = system_coordinator.agents.get("execution_agent")
    if execution_agent is None:
        return {}
    return {
        "cash": execution_agent.cash,
        "positions": execution_agent.portfolio,
        "broker": execution_agent.broker.name,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=API_CONFIG.get("reload", True),
    )
