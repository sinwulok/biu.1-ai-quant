"""
Risk Management Agent Module

This module implements risk management and portfolio analysis functionality.
"""

from typing import Dict, Any
from . import BaseAgent
from ..utils.analysis import (
    calculate_returns,
    calculate_volatility,
    calculate_sharpe_ratio
)

class RiskManagementAgent(BaseAgent):
    """
    Agent responsible for risk management and portfolio analysis.
    """
    
    def __init__(self, name: str, max_volatility: float = 0.2, min_sharpe: float = 1.0):
        super().__init__(name)
        self.max_volatility = max_volatility
        self.min_sharpe = min_sharpe
        self.portfolio_stats: Dict[str, Any] = {}

    def run(self) -> None:
        # Risk agent is reactive, no active loop needed
        pass

    def receive_message(self, message: Dict[str, Any]) -> None:
        if message['type'] == 'data_response':
            symbol = message['payload'].get('symbol')
            data = message['payload'].get('data')
            
            if data is not None:
                # Calculate risk metrics
                returns = calculate_returns(data['Close'].values)
                volatility = calculate_volatility(returns)
                sharpe = calculate_sharpe_ratio(returns)

                # Store statistics
                self.portfolio_stats[symbol] = {
                    'volatility': volatility,
                    'sharpe_ratio': sharpe,
                    'last_return': returns[-1] if len(returns) > 0 else 0
                }

                # Check risk limits
                if volatility > self.max_volatility:
                    self.send_message('decision_agent', 'risk_alert', {
                        'symbol': symbol,
                        'type': 'high_volatility',
                        'value': volatility,
                        'threshold': self.max_volatility
                    })

                if sharpe < self.min_sharpe:
                    self.send_message('decision_agent', 'risk_alert', {
                        'symbol': symbol,
                        'type': 'low_sharpe',
                        'value': sharpe,
                        'threshold': self.min_sharpe
                    })

        elif message['type'] == 'portfolio_update':
            # Request latest data for risk analysis
            positions = message['payload'].get('positions', {})
            for symbol in positions:
                self.send_message('data_agent', 'get_data', {
                    'symbol': symbol
                })
