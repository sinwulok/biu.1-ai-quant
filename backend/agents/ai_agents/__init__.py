"""
AI Agents Module

This package contains AI-based agent implementations for the trading system.
These agents use machine learning models for inference-driven decision making,
complementing or replacing the legacy rules-based agents in the parent package.
"""

from .model_inference_agent import ModelInferenceAgent

__all__ = [
    'ModelInferenceAgent',
]

__version__ = '0.1.0'
