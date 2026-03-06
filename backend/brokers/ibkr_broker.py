"""
IBKR Broker Adapter

Connects to Interactive Brokers via ib_insync (TWS / IB Gateway).
Only paper-trading is enabled by default; switch port to 7496 for live.

Requirements:
    pip install ib_insync

Setup:
    1. Launch TWS or IB Gateway and enable the API on port 7497 (paper).
    2. Set IBKR_CONFIG["enabled"] = True in backend/config.py.
"""

import uuid
import logging
from typing import Dict, Any

from .base_broker import BaseBroker, Order
from ..config import IBKR_CONFIG

logger = logging.getLogger(__name__)


class IBKRBroker(BaseBroker):
    """
    Interactive Brokers paper/live trading adapter using ib_insync.

    When ib_insync or TWS is not available the broker reports
    ``connected = False`` and all orders are rejected gracefully.
    """

    def __init__(self):
        super().__init__(
            name="ibkr",
            paper_trading=IBKR_CONFIG.get("paper_trading", True),
        )
        self._host: str = IBKR_CONFIG.get("host", "127.0.0.1")
        self._port: int = IBKR_CONFIG.get("port", 7497)
        self._client_id: int = IBKR_CONFIG.get("client_id", 1)
        self._ib = None  # ib_insync.IB instance

    # ------------------------------------------------------------------
    # BaseBroker interface
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        if not IBKR_CONFIG.get("enabled", False):
            logger.warning("IBKR broker is disabled in config (IBKR_CONFIG['enabled']=False).")
            return False
        try:
            from ib_insync import IB  # type: ignore
            self._ib = IB()
            self._ib.connect(self._host, self._port, clientId=self._client_id)
            self.connected = self._ib.isConnected()
            if self.connected:
                logger.info("IBKR connected (host=%s port=%d)", self._host, self._port)
            return self.connected
        except Exception as exc:
            logger.error("IBKR connect failed: %s", exc)
            self.connected = False
            return False

    def disconnect(self) -> None:
        if self._ib and self._ib.isConnected():
            self._ib.disconnect()
        self.connected = False

    def place_order(self, order: Order, **kwargs) -> Order:
        if not self.connected or self._ib is None:
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())
            logger.warning("IBKR place_order: not connected; order rejected.")
            return order

        try:
            from ib_insync import Stock, MarketOrder, LimitOrder  # type: ignore

            # Build IBKR contract (HK stocks use exchange SEHK)
            exchange = "SEHK" if order.symbol.endswith(".HK") else "SMART"
            currency = "HKD" if order.symbol.endswith(".HK") else "USD"
            ticker = order.symbol.replace(".HK", "")
            contract = Stock(ticker, exchange, currency)

            if order.order_type == "limit" and order.limit_price:
                ib_order = LimitOrder(order.action.upper(), order.quantity, order.limit_price)
            else:
                ib_order = MarketOrder(order.action.upper(), order.quantity)

            trade = self._ib.placeOrder(contract, ib_order)
            self._ib.sleep(1)  # allow IB to process

            order.order_id = str(trade.order.orderId)
            order.status = "filled" if trade.isDone() else "pending"
            if trade.fills:
                order.filled_price = trade.fills[-1].execution.price
                order.filled_quantity = trade.fills[-1].execution.shares
        except Exception as exc:
            logger.error("IBKR place_order error: %s", exc)
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())

        return order

    def cancel_order(self, order_id: str) -> bool:
        if not self.connected or self._ib is None:
            return False
        try:
            for trade in self._ib.openTrades():
                if str(trade.order.orderId) == order_id:
                    self._ib.cancelOrder(trade.order)
                    return True
        except Exception as exc:
            logger.error("IBKR cancel_order error: %s", exc)
        return False

    def get_positions(self) -> Dict[str, float]:
        if not self.connected or self._ib is None:
            return {}
        try:
            return {
                p.contract.symbol: p.position
                for p in self._ib.positions()
            }
        except Exception as exc:
            logger.error("IBKR get_positions error: %s", exc)
            return {}

    def get_account_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "broker": self.name,
            "paper_trading": self.paper_trading,
            "connected": self.connected,
        }
        if not self.connected or self._ib is None:
            return info
        try:
            account_values = self._ib.accountValues()
            for av in account_values:
                if av.tag in ("NetLiquidation", "TotalCashBalance") and av.currency == "HKD":
                    info[av.tag] = float(av.value)
        except Exception as exc:
            logger.error("IBKR get_account_info error: %s", exc)
        return info
