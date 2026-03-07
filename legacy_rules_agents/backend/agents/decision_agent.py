import time
from datetime import datetime
from .base_agent import BaseAgent


class DecisionAgent(BaseAgent):
  def __init__(self, name):
    super().__init__(name)
    self.strategy_signals = {}
    self.risk_reports = {}
    self.portfolio = {}

  def run(self):
    while self.running:
      # 每隔一段时间检查是否需要做决策
      self._check_pending_decisions()
      time.sleep(5)

  def receive_message(self, message):
    if message['type'] == 'strategy_signal':
      symbol = message['payload'].get('symbol')
      strategy = message['payload'].get('strategy')

      # 存储信号
      if symbol not in self.strategy_signals:
        self.strategy_signals[symbol] = {}

      self.strategy_signals[symbol][strategy] = {
          'signal': message['payload'].get('signal'),
          'strength': message['payload'].get('strength'),
          'timestamp': message['payload'].get('timestamp')
      }

      # 触发决策过程
      self._make_decision(symbol)

    elif message['type'] == 'risk_report':
      symbol = message['payload'].get('symbol')
      self.risk_reports[symbol] = message['payload']

  def _make_decision(self, symbol):
    # 简化的决策逻辑，可以更复杂
    if symbol in self.strategy_signals and 'MACD' in self.strategy_signals[symbol]:
      signal = self.strategy_signals[symbol]['MACD']['signal']

      # 考虑风险因素
      risk_ok = True
      if symbol in self.risk_reports:
        risk_level = self.risk_reports[symbol].get('risk_level', 'medium')
        if risk_level == 'high' and signal == 'buy':
          risk_ok = False

      if signal == 'buy' and risk_ok:
        # 发送交易指令
        self.send_message('execution_agent', 'trade_order', {
            'symbol': symbol,
            'action': 'buy',
            'quantity': 1,  # 简化，实际会基于资金管理计算
            'reason': 'MACD buy signal'
        })
      elif signal == 'sell':
        # 检查是否持有
        if symbol in self.portfolio and self.portfolio[symbol] > 0:
          self.send_message('execution_agent', 'trade_order', {
              'symbol': symbol,
              'action': 'sell',
              'quantity': self.portfolio.get(symbol, 0),
              'reason': 'MACD sell signal'
          })

  def _check_pending_decisions(self):
    # 检查是否有积压的决策需要处理
    current_time = datetime.now().strftime('%Y-%m-%d')
    for symbol in self.strategy_signals:
      last_decision_time = self.strategy_signals[symbol].get(
          'MACD', {}).get('timestamp', '')
      if last_decision_time != current_time:
        self._make_decision(symbol)
