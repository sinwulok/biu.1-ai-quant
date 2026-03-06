"""
YFinance Data Source

Fetches OHLCV data for HK stocks and global equities using yfinance.
Supports HK symbols in the format XXXXX.HK (e.g., 0700.HK for Tencent).
"""

import logging
from typing import Optional, List, Dict
import pandas as pd
import yfinance as yf

from ..config import YFINANCE_CONFIG

logger = logging.getLogger(__name__)


class YFinanceSource:
    """
    Data source wrapper around yfinance.

    Handles HK (.HK suffix) and global equity symbols transparently.
    """

    def __init__(
        self,
        default_period: str = YFINANCE_CONFIG["default_period"],
        default_interval: str = YFINANCE_CONFIG["default_interval"],
    ):
        self.default_period = default_period
        self.default_interval = default_interval

    def fetch(
        self,
        symbol: str,
        period: Optional[str] = None,
        interval: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Download historical OHLCV data for a single symbol.

        Args:
            symbol:   Ticker symbol (e.g. '0700.HK', 'AAPL').
            period:   yfinance period string (e.g. '1y', '6mo').
            interval: yfinance interval string (e.g. '1d', '1h').

        Returns:
            DataFrame with columns [Open, High, Low, Close, Volume] or None on error.
        """
        _period = period or self.default_period
        _interval = interval or self.default_interval
        try:
            data = yf.download(symbol, period=_period, interval=_interval,
                               auto_adjust=True, progress=False)
            if data is None or data.empty:
                logger.warning("YFinance: no data returned for %s", symbol)
                return None
            # Flatten MultiIndex columns if present (yfinance ≥ 0.2)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data
        except Exception as exc:
            logger.error("YFinance fetch error for %s: %s", symbol, exc)
            return None

    def fetch_many(
        self,
        symbols: List[str],
        period: Optional[str] = None,
        interval: Optional[str] = None,
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch data for multiple symbols. Returns a dict of {symbol: DataFrame}.
        """
        return {sym: self.fetch(sym, period, interval) for sym in symbols}

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Return the most recent closing price for a symbol."""
        data = self.fetch(symbol, period="5d", interval="1d")
        if data is not None and not data.empty:
            return float(data["Close"].iloc[-1])
        return None
