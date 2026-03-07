"""
Data Agent Module for handling market data operations.
Supports YFinance (HK stocks and global equities) and CCXT (crypto).
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    import yfinance as yf
except ImportError as e:
    print(f"Error importing yfinance: {e}")
    print("Please ensure yfinance is installed: pip install yfinance")
    raise

from . import BaseAgent
from ..utils.indicators import (
    calculate_macd,
    calculate_rsi,
    calculate_bollinger_bands
)


class DataAgent(BaseAgent):
  """
  Agent responsible for fetching and managing market data.
  """
  
  def __init__(self, name: str, symbols: List[str], timeframe: str = '1d'):
    super().__init__(name)
    self.symbols = symbols
    self.timeframe = timeframe
    self.data_cache: Dict[str, pd.DataFrame] = {}
    self.update_interval = 60  # seconds
    self.indicators_cache: Dict[str, Dict[str, Any]] = {}

  def run(self) -> None:
    while self.running:
      try:
        for symbol in self.symbols:
          # 使用yfinance获取数据
          data: Optional[pd.DataFrame] = yf.download(
              symbol, period='1y', interval=self.timeframe)
          if data is not None and not data.empty:
            self.data_cache[symbol] = data
            # 计算技术指标
            self._calculate_indicators(symbol)
            # 通知其他代理数据已更新
            self.send_message('all', 'data_updated', {
                'symbol': symbol,
                'timeframe': self.timeframe,
                'last_date': data.index[-1].strftime('%Y-%m-%d')
            })
          else:
            self.send_message('all', 'error', {
                'source': self.name,
                'error': f'No data received for {symbol}'
            })
        time.sleep(self.update_interval)
      except Exception as e:
        self.send_message('all', 'error', {
            'source': self.name,
            'error': str(e)
        })

  def _calculate_indicators(self, symbol: str) -> None:
    """Calculate and cache technical indicators for a symbol."""
    if symbol not in self.data_cache:
        return

    data = self.data_cache[symbol]
    prices = data['Close'].values

    # Calculate indicators
    macd_line, signal_line, histogram = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    upper, middle, lower = calculate_bollinger_bands(prices)

    # Cache the results
    self.indicators_cache[symbol] = {
        'macd': {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        },
        'rsi': rsi,
        'bollinger_bands': {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    }

  def receive_message(self, message: Dict[str, Any]) -> None:
    if message['type'] == 'get_data':
      symbol = message['payload'].get('symbol')
      if symbol in self.data_cache:
        response_data = {
            'symbol': symbol,
            'data': self.data_cache[symbol],
        }
        # Include technical indicators if available
        if symbol in self.indicators_cache:
            response_data['indicators'] = self.indicators_cache[symbol]
        
        self.send_message(message['sender'], 'data_response', response_data)
