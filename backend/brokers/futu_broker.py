"""
FUTU Broker Adapter

Connects to Futu OpenD for HK paper/live trading via futu-openapi.

Requirements:
    pip install futu-openapi

Setup:
    1. Download and run Futu OpenD (https://openapi.futunn.com).
    2. Log in with your Futu account and enable paper trading.
    3. Set FUTU_CONFIG["enabled"] = True in backend/config.py.
"""

import uuid
import logging
from typing import Dict, Any

from .base_broker import BaseBroker, Order
from ..config import FUTU_CONFIG

logger = logging.getLogger(__name__)


class FUTUBroker(BaseBroker):
    """
    Futu (富途) HK paper/live trading adapter via futu-openapi.

    Falls back gracefully when OpenD is not available.
    """

    def __init__(self):
        super().__init__(
            name="futu",
            paper_trading=FUTU_CONFIG.get("paper_trading", True),
        )
        self._host: str = FUTU_CONFIG.get("host", "127.0.0.1")
        self._port: int = FUTU_CONFIG.get("port", 11111)
        self._market: str = FUTU_CONFIG.get("market", "HK")
        self._trd_ctx = None  # futu TradeContext
        self._acc_id: int = 0

    # ------------------------------------------------------------------
    # BaseBroker interface
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        if not FUTU_CONFIG.get("enabled", False):
            logger.warning("FUTU broker is disabled in config (FUTU_CONFIG['enabled']=False).")
            return False
        try:
            import futu as ft  # type: ignore

            env = ft.TrdEnv.SIMULATE if self.paper_trading else ft.TrdEnv.REAL
            self._trd_ctx = ft.OpenHKTradeContext(host=self._host, port=self._port)
            ret, data = self._trd_ctx.get_acc_list()
            if ret == ft.RET_OK and not data.empty:
                # Pick the first paper/live account matching trd_env
                env_str = "SIMULATE" if self.paper_trading else "REAL"
                filtered = data[data["trd_env"] == env_str]
                if not filtered.empty:
                    self._acc_id = int(filtered.iloc[0]["acc_id"])
                    self.connected = True
                    logger.info("FUTU connected (acc_id=%d env=%s)", self._acc_id, env_str)
                    return True
            logger.error("FUTU connect: no matching account found. ret=%s", ret)
            return False
        except Exception as exc:
            logger.error("FUTU connect failed: %s", exc)
            self.connected = False
            return False

    def disconnect(self) -> None:
        if self._trd_ctx:
            self._trd_ctx.close()
        self.connected = False

    def place_order(self, order: Order, **kwargs) -> Order:
        if not self.connected or self._trd_ctx is None:
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())
            logger.warning("FUTU place_order: not connected; order rejected.")
            return order

        try:
            import futu as ft  # type: ignore

            env = ft.TrdEnv.SIMULATE if self.paper_trading else ft.TrdEnv.REAL
            side = ft.TrdSide.BUY if order.action == "buy" else ft.TrdSide.SELL

            # Futu uses HK.XXXXX format; convert from YFinance XXXXX.HK
            code = f"HK.{order.symbol.replace('.HK', '').zfill(5)}"

            if order.order_type == "limit" and order.limit_price:
                order_type = ft.OrderType.NORMAL
                price = order.limit_price
            else:
                order_type = ft.OrderType.MARKET
                price = 0.0

            ret, data = self._trd_ctx.place_order(
                price=price,
                qty=order.quantity,
                code=code,
                trd_side=side,
                order_type=order_type,
                trd_env=env,
                acc_id=self._acc_id,
            )

            if ret == ft.RET_OK:
                order.order_id = str(data["order_id"][0])
                order.status = "pending"
            else:
                logger.error("FUTU place_order error: %s", data)
                order.status = "rejected"
                order.order_id = str(uuid.uuid4())

        except Exception as exc:
            logger.error("FUTU place_order exception: %s", exc)
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())

        return order

    def cancel_order(self, order_id: str) -> bool:
        if not self.connected or self._trd_ctx is None:
            return False
        try:
            import futu as ft  # type: ignore
            env = ft.TrdEnv.SIMULATE if self.paper_trading else ft.TrdEnv.REAL
            ret, _ = self._trd_ctx.modify_order(
                modify_order_op=ft.ModifyOrderOp.CANCEL,
                order_id=int(order_id),
                qty=0,
                price=0,
                trd_env=env,
                acc_id=self._acc_id,
            )
            return ret == ft.RET_OK
        except Exception as exc:
            logger.error("FUTU cancel_order error: %s", exc)
            return False

    def get_positions(self) -> Dict[str, float]:
        if not self.connected or self._trd_ctx is None:
            return {}
        try:
            import futu as ft  # type: ignore
            env = ft.TrdEnv.SIMULATE if self.paper_trading else ft.TrdEnv.REAL
            ret, data = self._trd_ctx.position_list_query(trd_env=env, acc_id=self._acc_id)
            if ret == ft.RET_OK and not data.empty:
                return {
                    row["code"].replace("HK.", "") + ".HK": float(row["qty"])
                    for _, row in data.iterrows()
                }
        except Exception as exc:
            logger.error("FUTU get_positions error: %s", exc)
        return {}

    def get_account_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "broker": self.name,
            "paper_trading": self.paper_trading,
            "connected": self.connected,
        }
        if not self.connected or self._trd_ctx is None:
            return info
        try:
            import futu as ft  # type: ignore
            env = ft.TrdEnv.SIMULATE if self.paper_trading else ft.TrdEnv.REAL
            ret, data = self._trd_ctx.accinfo_query(trd_env=env, acc_id=self._acc_id)
            if ret == ft.RET_OK and not data.empty:
                info["cash"] = float(data["cash"][0])
                info["total_assets"] = float(data["total_assets"][0])
        except Exception as exc:
            logger.error("FUTU get_account_info error: %s", exc)
        return info
