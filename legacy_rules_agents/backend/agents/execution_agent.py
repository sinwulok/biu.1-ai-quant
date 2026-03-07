"""
Execution Agent

Delegates order execution to the configured broker adapter.
Supports PaperBroker (default), IBKRBroker, FUTUBroker, and CCXTBroker.
"""

from . import BaseAgent, datetime
from ..brokers.base_broker import Order
from ..brokers.paper_broker import PaperBroker


class ExecutionAgent(BaseAgent):
    """
    Agent responsible for order execution via a pluggable broker adapter.

    paper_trading=True (default): uses the built-in PaperBroker.
    Pass a broker instance via the `broker` keyword to use IBKR, FUTU, or CCXT.
    """

    def __init__(self, name, broker=None, paper_trading=True):
        super().__init__(name)
        if broker is not None:
            self.broker = broker
        else:
            self.broker = PaperBroker()
            self.broker.connect()
        self.paper_trading = paper_trading

    # Keep legacy attributes for API compatibility
    @property
    def orders(self):
        return [o.to_dict() for o in self.broker.orders]

    @property
    def portfolio(self):
        return self.broker.get_positions()

    @property
    def cash(self):
        return self.broker.cash

    def run(self):
        pass

    def receive_message(self, message):
        if message['type'] == 'trade_order':
            symbol = message['payload'].get('symbol')
            action = message['payload'].get('action')
            quantity = message['payload'].get('quantity')
            price = message['payload'].get('price')

            order = Order(
                symbol=symbol,
                action=action,
                quantity=quantity,
                broker=self.broker.name,
            )
            filled = self.broker.place_order(order, reference_price=price or 100.0)

            if filled.status == 'filled':
                self.send_message('all', 'trade_executed', {
                    'symbol': symbol,
                    'action': action,
                    'quantity': filled.filled_quantity,
                    'price': filled.filled_price,
                    'broker': filled.broker,
                    'timestamp': filled.fill_timestamp.isoformat() if filled.fill_timestamp else None,
                })

