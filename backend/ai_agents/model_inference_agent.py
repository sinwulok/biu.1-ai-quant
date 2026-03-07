# STUB: ModelInferenceAgent - AI-first replacement for rule-based agents.
import os

from backend.legacy_rule_agents.backend.agents.base_agent import BaseAgent


class ModelInferenceAgent(BaseAgent):
    """Stub agent that handles 'inference_request' messages.

    When a trained model file is present it will be loaded and used for
    inference.  When no model file is found the agent falls back to a
    simple heuristic (buy/hold/sell based on the last price change sign).
    """

    def __init__(self, name: str = "model_inference_agent", model_path: str | None = None):
        super().__init__(name)
        self.model_path = model_path
        self.model = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self):
        """Entry-point called by BaseAgent.start() in a daemon thread."""
        self._load_model()

    def _load_model(self):
        """Attempt to load a model from *model_path*.  Silently skips when absent."""
        if self.model_path and os.path.exists(self.model_path):
            # TODO: replace with real model-loading logic (e.g. torch.load / joblib)
            self.model = object()  # placeholder

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def receive_message(self, message: dict):
        """Dispatch incoming messages by type."""
        if message.get("type") == "inference_request":
            response = self._handle_inference(message.get("payload", {}))
            self.send_message(
                message.get("sender", "coordinator"),
                "inference_response",
                response,
            )

    def _handle_inference(self, payload: dict) -> dict:
        """Return an inference result dict.

        Uses the loaded model when available; otherwise applies a
        heuristic fallback based on *price_change* in the payload.
        """
        if self.model is not None:
            # TODO: call real model.predict(payload) here
            return {"signal": "hold", "confidence": 0.0, "source": "model"}

        # --- heuristic fallback ---
        price_change = payload.get("price_change", 0)
        if price_change > 0:
            signal = "buy"
        elif price_change < 0:
            signal = "sell"
        else:
            signal = "hold"
        return {"signal": signal, "confidence": 0.0, "source": "heuristic_fallback"}
