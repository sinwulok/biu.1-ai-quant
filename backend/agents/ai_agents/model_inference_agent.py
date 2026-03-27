"""
Model Inference Agent

Stub implementation of an AI-based trading agent that delegates buy/sell/hold
decisions to a pluggable machine-learning model.  Replace or extend this class
to integrate your own model (e.g. scikit-learn, PyTorch, ONNX Runtime).
"""

from typing import Any, Dict, Optional

from ..base_agent import BaseAgent


class ModelInferenceAgent(BaseAgent):
    """
    An agent that generates trading signals by running inference on an ML model.

    Usage
    -----
    Subclass this agent and override :meth:`_predict` to call your model:

    .. code-block:: python

        class MyModelAgent(ModelInferenceAgent):
            def _predict(self, features: Dict[str, Any]) -> str:
                prob = self.model.predict_proba([list(features.values())])[0]
                return 'buy' if prob[1] > 0.6 else 'sell' if prob[1] < 0.4 else 'hold'

    Parameters
    ----------
    name : str
        Agent name used for message routing.
    model : optional
        A pre-loaded model object that exposes a ``predict`` (or similar) API.
        Defaults to ``None``; swap in your model at construction time.
    """

    def __init__(self, name: str, model: Optional[Any] = None):
        super().__init__(name)
        self.model = model

    # ------------------------------------------------------------------
    # Agent lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Inference agents are reactive; no active polling loop required."""
        pass

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def receive_message(self, message: Dict[str, Any]) -> None:
        """React to incoming messages from other agents."""
        if message['type'] == 'data_response':
            symbol = message['payload'].get('symbol')
            data = message['payload'].get('data')
            indicators = message['payload'].get('indicators', {})

            if data is not None:
                features = self._extract_features(data, indicators)
                signal = self._predict(features)
                self.send_message('decision_agent', 'strategy_signal', {
                    'symbol': symbol,
                    'strategy': 'ModelInference',
                    'signal': signal,
                    'strength': 1.0,
                    'timestamp': str(data.index[-1].date()),
                })

        elif message['type'] == 'data_updated':
            symbol = message['payload'].get('symbol')
            self.send_message('data_agent', 'get_data', {'symbol': symbol})

    # ------------------------------------------------------------------
    # Overridable helpers
    # ------------------------------------------------------------------

    def _extract_features(
        self,
        data: Any,
        indicators: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a feature dictionary from raw OHLCV data and pre-computed
        technical indicators.  Override this method to customise the feature
        set fed into the model.
        """
        features: Dict[str, Any] = {}

        # Latest close price
        features['close'] = float(data['Close'].iloc[-1])

        # MACD histogram (last value)
        macd = indicators.get('macd', {})
        histogram = macd.get('histogram')
        if histogram is not None and len(histogram) > 0:
            features['macd_histogram'] = float(histogram[-1])

        # RSI (last value)
        rsi = indicators.get('rsi')
        if rsi is not None and len(rsi) > 0:
            features['rsi'] = float(rsi[-1])

        return features

    def _predict(self, features: Dict[str, Any]) -> str:
        """
        Run model inference on the extracted features and return a signal.

        Returns one of ``'buy'``, ``'sell'``, or ``'hold'``.

        Override this method in a subclass to call your actual model.
        The default stub always returns ``'hold'``.
        """
        if self.model is None:
            return 'hold'

        # TODO: replace with real model call, e.g.:
        #   prediction = self.model.predict([list(features.values())])
        #   return prediction[0]
        return 'hold'
