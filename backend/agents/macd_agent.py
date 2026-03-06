"""
MACD Strategy Agent Module

This module implements a trading strategy based on the MACD (Moving Average Convergence Divergence) indicator.
"""

from typing import Dict, Any
from . import BaseAgent
from ..utils.indicators import calculate_macd


class MACDStrategyAgent(BaseAgent):
  """
  A trading agent that generates signals based on MACD crossovers.
  """
  
  def __init__(self, name: str, fast: int = 12, slow: int = 26, signal: int = 9):
    super().__init__(name)
    self.fast = fast
    self.slow = slow
    self.signal = signal
    self.signals: Dict[str, Any] = {}

  def run(self):
    # 策略代理主要是响应式的，不需要主动循环
    pass

  def receive_message(self, message):
    if message['type'] == 'data_updated':
      symbol = message['payload'].get('symbol')
      # 请求完整数据
      self.send_message('data_agent', 'get_data', {
          'symbol': symbol
      })

    elif message['type'] == 'data_response':
      symbol = message['payload'].get('symbol')
      data = message['payload'].get('data')
      if data is not None:
        # 计算MACD
        prices = data['Close'].values
        macd_line, signal_line, histogram = calculate_macd(
            prices, 
            fast_period=self.fast,
            slow_period=self.slow,
            signal_period=self.signal
        )

        # 生成交易信号
        previous_hist = histogram[-2]
        current_hist = histogram[-1]

        # 判断柱状图穿越零线
        if previous_hist < 0 and current_hist > 0:
          signal_type = 'buy'
        elif previous_hist > 0 and current_hist < 0:
          signal_type = 'sell'
        else:
          signal_type = 'hold'

        # 发送信号到决策代理
        self.send_message('decision_agent', 'strategy_signal', {
            'symbol': symbol,
            'strategy': 'MACD',
            'signal': signal_type,
            'strength': abs(current_hist),
            'timestamp': data.index[-1].strftime('%Y-%m-%d')
        })
