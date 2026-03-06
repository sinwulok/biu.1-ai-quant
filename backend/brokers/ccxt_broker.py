"""
CCXT Broker Adapter

Connects to crypto exchanges via the ccxt library for paper/live crypto trading.

Requirements:
    pip install ccxt

Setup:
    1. Set CCXT_BROKER_CONFIG["exchange"] to your target exchange.
    2. Set CCXT_BROKER_CONFIG["api_key"] and ["secret"] (use env vars in production).
    3. Set CCXT_BROKER_CONFIG["enabled"] = True in backend/config.py.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any

from .base_broker import BaseBroker, Order
from ..config import CCXT_BROKER_CONFIG

logger = logging.getLogger(__name__)


class CCXTBroker(BaseBroker):
    """
    Crypto exchange broker adapter via ccxt.

    Supports both sandbox (paper) and live modes depending on exchange support.
    """

    def __init__(self):
        super().__init__(
            name="ccxt",
            paper_trading=CCXT_BROKER_CONFIG.get("sandbox", True),
        )
        self._exchange_id: str = CCXT_BROKER_CONFIG.get("exchange", "binance")
        self._api_key: str = CCXT_BROKER_CONFIG.get("api_key", "")
        self._secret: str = CCXT_BROKER_CONFIG.get("secret", "")
        self._sandbox: bool = CCXT_BROKER_CONFIG.get("sandbox", True)
        self._exchange = None

    # ------------------------------------------------------------------
    # BaseBroker interface
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        if not CCXT_BROKER_CONFIG.get("enabled", False):
            logger.warning("CCXT broker is disabled in config (CCXT_BROKER_CONFIG['enabled']=False).")
            return False
        try:
            import ccxt  # type: ignore

            exchange_class = getattr(ccxt, self._exchange_id)
            self._exchange = exchange_class({
                "apiKey": self._api_key,
                "secret": self._secret,
                "enableRateLimit": True,
            })
            if self._sandbox and self._exchange.has.get("sandbox"):
                self._exchange.set_sandbox_mode(True)
            self._exchange.load_markets()
            self.connected = True
            logger.info("CCXT connected to %s (sandbox=%s)", self._exchange_id, self._sandbox)
            return True
        except Exception as exc:
            logger.error("CCXT connect failed: %s", exc)
            self.connected = False
            return False

    def disconnect(self) -> None:
        self._exchange = None
        self.connected = False

    def place_order(self, order: Order, **kwargs) -> Order:
        if not self.connected or self._exchange is None:
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())
            logger.warning("CCXT place_order: not connected; order rejected.")
            return order

        try:
            if order.order_type == "limit" and order.limit_price:
                result = self._exchange.create_order(
                    order.symbol, "limit", order.action, order.quantity, order.limit_price
                )
            else:
                result = self._exchange.create_order(
                    order.symbol, "market", order.action, order.quantity
                )

            order.order_id = str(result.get("id", uuid.uuid4()))
            order.status = result.get("status", "pending")
            if result.get("average"):
                order.filled_price = float(result["average"])
                order.filled_quantity = float(result.get("filled", order.quantity))
                order.fill_timestamp = datetime.now()

        except Exception as exc:
            logger.error("CCXT place_order error: %s", exc)
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())

        return order

    def cancel_order(self, order_id: str) -> bool:
        if not self.connected or self._exchange is None:
            return False
        try:
            self._exchange.cancel_order(order_id)
            return True
        except Exception as exc:
            logger.error("CCXT cancel_order error: %s", exc)
            return False

    def get_positions(self) -> Dict[str, float]:
        if not self.connected or self._exchange is None:
            return {}
        try:
            balance = self._exchange.fetch_balance()
            return {
                asset: float(info["free"])
                for asset, info in balance.items()
                if isinstance(info, dict) and float(info.get("free", 0)) > 0
            }
        except Exception as exc:
            logger.error("CCXT get_positions error: %s", exc)
            return {}

    def get_account_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "broker": self.name,
            "paper_trading": self.paper_trading,
            "connected": self.connected,
            "exchange": self._exchange_id,
        }
        if not self.connected or self._exchange is None:
            return info
        try:
            balance = self._exchange.fetch_balance()
            info["total"] = balance.get("total", {})
            info["free"] = balance.get("free", {})
        except Exception as exc:
            logger.error("CCXT get_account_info error: %s", exc)
        return info
