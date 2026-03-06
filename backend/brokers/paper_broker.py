"""
Paper Broker

A built-in paper-trading broker that simulates order execution without
requiring any external connections. Used as the default broker in simulation
mode or when IBKR/FUTU/CCXT are not configured.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .base_broker import BaseBroker, Order
from ..config import SIMULATION_CONFIG


class PaperBroker(BaseBroker):
    """
    In-process paper trading broker.

    Fills market orders at the provided reference price, applying configurable
    commission, stamp duty, and slippage.
    """

    def __init__(self, initial_capital: float = SIMULATION_CONFIG["initial_capital"]):
        super().__init__(name="paper", paper_trading=True)
        self.cash = initial_capital
        self.positions: Dict[str, float] = {}
        self.orders: list = []

        self._commission_rate: float = SIMULATION_CONFIG["commission_rate"]
        self._stamp_duty_rate: float = SIMULATION_CONFIG["stamp_duty_rate"]
        self._slippage_bps: float = SIMULATION_CONFIG["slippage_bps"]

    # ------------------------------------------------------------------
    # BaseBroker interface
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    def place_order(self, order: Order, reference_price: Optional[float] = None) -> Order:
        """
        Simulate order execution.

        Args:
            order: The order to execute.
            reference_price: Last known market price. If None, order is rejected.
        """
        if reference_price is None or reference_price <= 0:
            order.status = "rejected"
            order.order_id = str(uuid.uuid4())
            self.orders.append(order)
            return order

        slippage = reference_price * self._slippage_bps / 10_000
        if order.action == "buy":
            fill_price = reference_price + slippage
        else:
            fill_price = reference_price - slippage

        gross = fill_price * order.quantity
        commission = gross * self._commission_rate
        stamp_duty = gross * self._stamp_duty_rate if order.action == "buy" else 0.0
        total_cost = gross + commission + stamp_duty

        if order.action == "buy":
            if total_cost > self.cash:
                order.status = "rejected"
            else:
                self.cash -= total_cost
                self.positions[order.symbol] = self.positions.get(order.symbol, 0.0) + order.quantity
                order.status = "filled"
                order.filled_price = fill_price
                order.filled_quantity = order.quantity
                order.fill_timestamp = datetime.now()

        elif order.action == "sell":
            held = self.positions.get(order.symbol, 0.0)
            if held < order.quantity:
                order.status = "rejected"
            else:
                proceeds = gross - commission
                self.cash += proceeds
                self.positions[order.symbol] = held - order.quantity
                if self.positions[order.symbol] == 0:
                    del self.positions[order.symbol]
                order.status = "filled"
                order.filled_price = fill_price
                order.filled_quantity = order.quantity
                order.fill_timestamp = datetime.now()
        else:
            order.status = "rejected"

        order.order_id = str(uuid.uuid4())
        self.orders.append(order)
        return order

    def cancel_order(self, order_id: str) -> bool:
        for o in self.orders:
            if o.order_id == order_id and o.status == "pending":
                o.status = "cancelled"
                return True
        return False

    def get_positions(self) -> Dict[str, float]:
        return dict(self.positions)

    def get_account_info(self) -> Dict[str, Any]:
        return {
            "broker": self.name,
            "paper_trading": True,
            "cash": self.cash,
            "positions": self.get_positions(),
        }
