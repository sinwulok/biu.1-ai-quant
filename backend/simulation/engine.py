"""
Simulation Engine

Event-driven backtesting and paper-trading simulation engine.
Supports HK stocks (via YFinance), crypto (via CCXT), and uses PaperBroker
for order execution to ensure realistic commission/stamp-duty accounting.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

import numpy as np
import pandas as pd

from ..data.yfinance_source import YFinanceSource
from ..data.ccxt_source import CCXTSource
from ..brokers.paper_broker import PaperBroker
from ..brokers.base_broker import Order
from ..utils.analysis import (
    calculate_returns,
    calculate_volatility,
    calculate_sharpe_ratio,
    perform_backtest,
)
from ..config import SIMULATION_CONFIG, HK_DEFAULT_SYMBOLS

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Runs a strategy simulation (backtest or paper-trading) over historical or
    live data.

    Usage (backtest)::

        engine = SimulationEngine(symbols=["0700.HK", "0005.HK"])
        engine.set_strategy(my_strategy_fn)
        results = engine.run_backtest(period="1y")

    Usage (paper-trading)::

        engine = SimulationEngine(symbols=["0700.HK"])
        engine.set_strategy(my_strategy_fn)
        engine.run_paper()      # blocks until stopped

    Strategy function signature::

        def my_strategy(engine: SimulationEngine,
                        symbol: str,
                        data: pd.DataFrame) -> Optional[str]:
            # return 'buy', 'sell', or None
    """

    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        data_source: str = "yfinance",
        initial_capital: float = SIMULATION_CONFIG["initial_capital"],
    ):
        self.symbols: List[str] = symbols or HK_DEFAULT_SYMBOLS
        self.data_source_name = data_source
        self.broker = PaperBroker(initial_capital=initial_capital)
        self.broker.connect()

        self._yf_source = YFinanceSource()
        self._ccxt_source: Optional[CCXTSource] = None
        if data_source == "ccxt":
            self._ccxt_source = CCXTSource()

        self._strategy_fn: Optional[Callable] = None
        self._data_cache: Dict[str, pd.DataFrame] = {}

        self.trade_log: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []

        self._running = False

    # ------------------------------------------------------------------
    # Strategy Registration
    # ------------------------------------------------------------------

    def set_strategy(self, fn: Callable) -> None:
        """Register a strategy function."""
        self._strategy_fn = fn

    # ------------------------------------------------------------------
    # Data Fetching
    # ------------------------------------------------------------------

    def load_data(
        self,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """Fetch historical OHLCV data for all configured symbols."""
        if self.data_source_name == "ccxt" and self._ccxt_source:
            self._data_cache = self._ccxt_source.fetch_many(self.symbols)
        else:
            self._data_cache = self._yf_source.fetch_many(
                self.symbols, period=period, interval=interval
            )
        loaded = sum(1 for v in self._data_cache.values() if v is not None)
        logger.info("Loaded data for %d / %d symbols", loaded, len(self.symbols))
        return self._data_cache

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Return the latest price for a symbol from the cache or live."""
        if symbol in self._data_cache and self._data_cache[symbol] is not None:
            df = self._data_cache[symbol]
            if not df.empty:
                return float(df["Close"].iloc[-1])
        if self.data_source_name == "ccxt" and self._ccxt_source:
            return self._ccxt_source.get_latest_price(symbol)
        return self._yf_source.get_latest_price(symbol)

    # ------------------------------------------------------------------
    # Backtest
    # ------------------------------------------------------------------

    def run_backtest(
        self,
        period: str = "1y",
        interval: str = "1d",
    ) -> Dict[str, Any]:
        """
        Run a vectorised walk-forward backtest over historical data.

        Returns a results dict with PnL, Sharpe, drawdown, and trade log.
        """
        logger.info("Starting backtest (period=%s interval=%s)", period, interval)
        self.load_data(period=period, interval=interval)

        if self._strategy_fn is None:
            raise RuntimeError("No strategy set. Call set_strategy() first.")

        self.trade_log.clear()
        self.equity_curve.clear()

        for symbol, df in self._data_cache.items():
            if df is None or len(df) < 30:
                logger.warning("Insufficient data for %s, skipping.", symbol)
                continue

            for i in range(30, len(df)):
                window = df.iloc[:i]
                signal = self._strategy_fn(self, symbol, window)
                price = float(df["Close"].iloc[i])

                if signal in ("buy", "sell"):
                    qty = self._calc_quantity(symbol, signal, price)
                    if qty > 0:
                        order = Order(
                            symbol=symbol,
                            action=signal,
                            quantity=qty,
                            broker="paper",
                        )
                        filled = self.broker.place_order(order, reference_price=price)
                        if filled.status == "filled":
                            entry = filled.to_dict()
                            entry["bar_index"] = i
                            entry["bar_date"] = df.index[i].isoformat()
                            self.trade_log.append(entry)

                # Record equity snapshot
                equity = self._calc_equity()
                self.equity_curve.append({
                    "date": df.index[i].isoformat(),
                    "equity": equity,
                })

        results = self._compile_results()
        logger.info(
            "Backtest complete — total_return=%.2f%% sharpe=%.2f trades=%d",
            results["total_return_pct"],
            results["sharpe_ratio"],
            results["num_trades"],
        )
        return results

    # ------------------------------------------------------------------
    # Paper Trading (live mode)
    # ------------------------------------------------------------------

    def run_paper(self, interval_seconds: int = 60) -> None:
        """
        Run continuous paper trading. Fetches fresh data at each interval
        and applies the strategy. Blocks until stop() is called.
        """
        import time

        if self._strategy_fn is None:
            raise RuntimeError("No strategy set. Call set_strategy() first.")

        self._running = True
        logger.info("Paper trading started (refresh every %ds)", interval_seconds)

        while self._running:
            self.load_data(period="60d", interval="1d")
            for symbol, df in self._data_cache.items():
                if df is None or df.empty:
                    continue
                signal = self._strategy_fn(self, symbol, df)
                price = self.get_latest_price(symbol)
                if signal in ("buy", "sell") and price:
                    qty = self._calc_quantity(symbol, signal, price)
                    if qty > 0:
                        order = Order(
                            symbol=symbol,
                            action=signal,
                            quantity=qty,
                            broker="paper",
                        )
                        filled = self.broker.place_order(order, reference_price=price)
                        if filled.status == "filled":
                            entry = filled.to_dict()
                            entry["bar_date"] = datetime.now().isoformat()
                            self.trade_log.append(entry)
                            logger.info("Paper trade: %s %s x%.0f @ %.4f",
                                        signal, symbol, qty, filled.filled_price)

            equity = self._calc_equity()
            self.equity_curve.append({
                "date": datetime.now().isoformat(),
                "equity": equity,
            })
            time.sleep(interval_seconds)

    def stop(self) -> None:
        """Stop the paper-trading loop."""
        self._running = False

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _calc_quantity(self, symbol: str, action: str, price: float) -> float:
        """Calculate order quantity based on position sizing rules."""
        max_pct = SIMULATION_CONFIG["max_position_pct"]
        cash = self.broker.cash
        positions = self.broker.get_positions()
        max_value = (cash + self._positions_value()) * max_pct

        if action == "buy":
            qty = max_value / price if price > 0 else 0
            return max(0.0, qty)
        elif action == "sell":
            return positions.get(symbol, 0.0)
        return 0.0

    def _positions_value(self) -> float:
        """Estimate total market value of open positions."""
        total = 0.0
        for sym, qty in self.broker.get_positions().items():
            price = self.get_latest_price(sym) or 0.0
            total += qty * price
        return total

    def _calc_equity(self) -> float:
        return self.broker.cash + self._positions_value()

    def _compile_results(self) -> Dict[str, Any]:
        """Compile backtest performance metrics."""
        if len(self.equity_curve) < 2:
            return {
                "total_return_pct": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "num_trades": len(self.trade_log),
                "final_equity": self._calc_equity(),
                "equity_curve": self.equity_curve,
                "trade_log": self.trade_log,
            }

        equities = np.array([e["equity"] for e in self.equity_curve])
        returns = calculate_returns(equities)

        total_return = (equities[-1] / equities[0]) - 1
        sharpe = calculate_sharpe_ratio(returns) if len(returns) > 1 else 0.0

        # Max drawdown
        peak = np.maximum.accumulate(equities)
        drawdown = (equities - peak) / peak
        max_dd = float(drawdown.min())

        return {
            "total_return_pct": round(total_return * 100, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "num_trades": len(self.trade_log),
            "final_equity": round(equities[-1], 2),
            "equity_curve": self.equity_curve,
            "trade_log": self.trade_log,
        }

    def get_status(self) -> Dict[str, Any]:
        """Return current simulation status for the API."""
        return {
            "running": self._running,
            "data_source": self.data_source_name,
            "symbols": self.symbols,
            "account": self.broker.get_account_info(),
            "num_trades": len(self.trade_log),
            "equity": self._calc_equity(),
        }
