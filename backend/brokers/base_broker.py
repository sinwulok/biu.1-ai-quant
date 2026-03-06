"""
Base Broker Interface

Defines the abstract contract that all broker adapters must implement.
Both paper-trading and live-trading adapters inherit from this class.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any


class Order:
    """Represents a single order."""

    def __init__(
        self,
        symbol: str,
        action: str,           # 'buy' | 'sell'
        quantity: float,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        broker: str = "paper",
    ):
        self.symbol = symbol
        self.action = action
        self.quantity = quantity
        self.order_type = order_type
        self.limit_price = limit_price
        self.broker = broker
        self.status = "pending"   # pending | filled | rejected | cancelled
        self.filled_price: Optional[float] = None
        self.filled_quantity: float = 0.0
        self.timestamp = datetime.now()
        self.fill_timestamp: Optional[datetime] = None
        self.order_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "limit_price": self.limit_price,
            "broker": self.broker,
            "status": self.status,
            "filled_price": self.filled_price,
            "filled_quantity": self.filled_quantity,
            "timestamp": self.timestamp.isoformat(),
            "fill_timestamp": self.fill_timestamp.isoformat() if self.fill_timestamp else None,
        }


class BaseBroker(ABC):
    """
    Abstract base class for all broker adapters.

    Implementations:
        - PaperBroker      – built-in simulation (no external dependency)
        - IBKRBroker       – Interactive Brokers via ib_insync
        - FUTUBroker       – Futu OpenD via futu-openapi
        - CCXTBroker       – Crypto exchanges via ccxt
    """

    def __init__(self, name: str, paper_trading: bool = True):
        self.name = name
        self.paper_trading = paper_trading
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the broker. Returns True on success."""

    @abstractmethod
    def disconnect(self) -> None:
        """Gracefully close the broker connection."""

    @abstractmethod
    def place_order(self, order: Order) -> Order:
        """Submit an order. Returns the order with updated status/fill fields."""

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order by ID."""

    @abstractmethod
    def get_positions(self) -> Dict[str, float]:
        """Return current positions as {symbol: quantity}."""

    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Return account balance and equity info."""

    def is_connected(self) -> bool:
        return self.connected
