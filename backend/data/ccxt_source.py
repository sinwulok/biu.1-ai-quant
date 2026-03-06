"""
CCXT Data Source

Fetches OHLCV data for crypto assets via the ccxt library.

Requirements:
    pip install ccxt
"""

import logging
from typing import Optional, Dict, List
import pandas as pd

from ..config import CCXT_CONFIG

logger = logging.getLogger(__name__)


class CCXTSource:
    """
    Data source wrapper around ccxt for crypto OHLCV data.

    Works without API keys for public market data endpoints.
    """

    def __init__(
        self,
        exchange_id: str = CCXT_CONFIG["default_exchange"],
        default_timeframe: str = CCXT_CONFIG["default_timeframe"],
    ):
        self._exchange_id = exchange_id
        self.default_timeframe = default_timeframe
        self._exchange = None
        self._init_exchange()

    def _init_exchange(self) -> None:
        try:
            import ccxt  # type: ignore

            exchange_class = getattr(ccxt, self._exchange_id)
            self._exchange = exchange_class({"enableRateLimit": True})
            self._exchange.load_markets()
            logger.info("CCXTSource initialised with exchange: %s", self._exchange_id)
        except ImportError:
            logger.warning("ccxt is not installed. CCXTSource will return no data.")
        except Exception as exc:
            logger.error("CCXTSource init error: %s", exc)

    def fetch(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
        limit: int = 500,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV candles for a crypto symbol.

        Args:
            symbol:    CCXT-format symbol (e.g. 'BTC/USDT').
            timeframe: Timeframe string (e.g. '1d', '1h', '15m').
            limit:     Number of candles to fetch.

        Returns:
            DataFrame with columns [Open, High, Low, Close, Volume] or None on error.
        """
        if self._exchange is None:
            return None

        _timeframe = timeframe or self.default_timeframe
        try:
            ohlcv = self._exchange.fetch_ohlcv(symbol, timeframe=_timeframe, limit=limit)
            if not ohlcv:
                logger.warning("CCXTSource: no data for %s", symbol)
                return None
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as exc:
            logger.error("CCXTSource fetch error for %s: %s", symbol, exc)
            return None

    def fetch_many(
        self,
        symbols: List[str],
        timeframe: Optional[str] = None,
        limit: int = 500,
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """Fetch data for multiple crypto symbols."""
        return {sym: self.fetch(sym, timeframe, limit) for sym in symbols}

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Return the latest bid price for a crypto symbol."""
        if self._exchange is None:
            return None
        try:
            ticker = self._exchange.fetch_ticker(symbol)
            return float(ticker.get("last") or ticker.get("close", 0))
        except Exception as exc:
            logger.error("CCXTSource get_latest_price error for %s: %s", symbol, exc)
            return None
