"""
Brokers Package

Provides broker adapters for:
  - PaperBroker  – built-in simulation (default)
  - IBKRBroker   – Interactive Brokers (HK & global equities)
  - FUTUBroker   – Futu OpenD (HK stocks)
  - CCXTBroker   – Crypto exchanges via ccxt
"""

from .base_broker import BaseBroker, Order
from .paper_broker import PaperBroker
from .ibkr_broker import IBKRBroker
from .futu_broker import FUTUBroker
from .ccxt_broker import CCXTBroker

__all__ = [
    "BaseBroker",
    "Order",
    "PaperBroker",
    "IBKRBroker",
    "FUTUBroker",
    "CCXTBroker",
]
