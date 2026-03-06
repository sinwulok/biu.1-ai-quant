"""
Configuration Module

Central configuration for the HK-focused automated trading simulation platform.
Covers market settings, broker adapters (IBKR, FUTU, CCXT), and data sources (YFinance, CCXT).
"""

from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# HK Market Configuration
# ---------------------------------------------------------------------------

HK_MARKET = {
    "name": "HKEX",
    "timezone": "Asia/Hong_Kong",
    "open_time": "09:30",
    "close_time": "16:00",
    "lunch_break_start": "12:00",
    "lunch_break_end": "13:00",
    "currency": "HKD",
    "lot_size_default": 100,
}

HK_DEFAULT_SYMBOLS: List[str] = [
    "0700.HK",   # Tencent
    "0005.HK",   # HSBC
    "0941.HK",   # China Mobile
    "1299.HK",   # AIA
    "0388.HK",   # HKEX
    "2318.HK",   # Ping An Insurance
    "0003.HK",   # HK & China Gas
    "1398.HK",   # ICBC
    "0001.HK",   # CK Hutchison
    "0016.HK",   # Sun Hung Kai Properties
]

# ---------------------------------------------------------------------------
# Data Source Configuration
# ---------------------------------------------------------------------------

YFINANCE_CONFIG: Dict[str, Any] = {
    "default_period": "1y",
    "default_interval": "1d",
    "supported_intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "90m",
                            "1h", "1d", "5d", "1wk", "1mo", "3mo"],
}

CCXT_CONFIG: Dict[str, Any] = {
    "default_exchange": "binance",
    "default_symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
    "default_timeframe": "1d",
    "sandbox": True,
}

# ---------------------------------------------------------------------------
# Broker Configuration
# ---------------------------------------------------------------------------

IBKR_CONFIG: Dict[str, Any] = {
    "host": "127.0.0.1",
    "port": 7497,          # 7497 = paper trading; 7496 = live
    "client_id": 1,
    "paper_trading": True,
    "account": "",
    "currency": "HKD",
    "enabled": False,
}

FUTU_CONFIG: Dict[str, Any] = {
    "host": "127.0.0.1",
    "port": 11111,
    "paper_trading": True,
    "market": "HK",
    "currency": "HKD",
    "enabled": False,
}

CCXT_BROKER_CONFIG: Dict[str, Any] = {
    "exchange": "binance",
    "api_key": "",
    "secret": "",
    "sandbox": True,
    "enabled": False,
}

# ---------------------------------------------------------------------------
# Simulation / Backtesting Configuration
# ---------------------------------------------------------------------------

SIMULATION_CONFIG: Dict[str, Any] = {
    "initial_capital": 1_000_000.0,   # HKD
    "commission_rate": 0.0012,
    "stamp_duty_rate": 0.0013,
    "slippage_bps": 5,
    "max_position_pct": 0.10,         # max 10% of total portfolio value per position
    "risk_free_rate": 0.04,
}

# ---------------------------------------------------------------------------
# Agent / Strategy Configuration
# ---------------------------------------------------------------------------

MACD_CONFIG: Dict[str, Any] = {
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9,
}

RSI_CONFIG: Dict[str, Any] = {
    "period": 14,
    "oversold": 30,
    "overbought": 70,
}

BOLLINGER_CONFIG: Dict[str, Any] = {
    "period": 20,
    "num_std": 2.0,
}

RISK_CONFIG: Dict[str, Any] = {
    "max_volatility": 0.30,
    "min_sharpe": 0.5,
    "max_drawdown": 0.15,
}

# ---------------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------------

API_CONFIG: Dict[str, Any] = {
    "host": "0.0.0.0",
    "port": 28000,
    "reload": True,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
}
