"""
SiuBiu-AI-Quant-System Agents Module

This package contains all the agent implementations for the trading system.
"""

# Core Python imports
import time
from datetime import datetime
from queue import Queue

# Base agent and coordinator
from .base_agent import BaseAgent
from .coordinator import AgentCoordinator

# Strategy and execution agents
from .data_agent import DataAgent
from .macd_agent import MACDStrategyAgent
from .decision_agent import DecisionAgent
from .execution_agent import ExecutionAgent
from .risk_agent import RiskManagementAgent

__all__ = [
  # Base classes
  'BaseAgent',
  'AgentCoordinator',

  # Agent implementations
  'DataAgent',
  'MACDStrategyAgent',
  'DecisionAgent',
  'ExecutionAgent',
  'RiskManagementAgent',

  # Core utilities
  'time',
  'datetime',
  'Queue'
]

# Agents version
__version__ = '0.1.4'
