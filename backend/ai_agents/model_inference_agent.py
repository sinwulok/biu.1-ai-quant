"""
ModelInferenceAgent – starter stub for AI-first inference.

STUB: implementation is intentionally minimal.  Replace the heuristic
fallback with a real model call when a model is available.
"""

import sys
import os

# Allow importing from the moved legacy package or from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from legacy_rule_agents.base_agent import BaseAgent  # type: ignore


class ModelInferenceAgent(BaseAgent):
    """AI-first agent that handles 'inference_request' messages.

    When a trained model is not available it falls back to a simple
    heuristic so the pipeline can still run end-to-end.

    STUB – replace ``_model_predict`` with real model inference.
    """

    def __init__(self, name: str = "model_inference_agent", model=None):
        super().__init__(name)
        self.model = model  # set to a loaded model object when available

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def receive_message(self, message: dict) -> None:
        if message.get("type") == "inference_request":
            payload = message.get("payload", {})
            result = self._run_inference(payload)
            self.send_message(
                message.get("sender", "coordinator"),
                "inference_response",
                result,
            )

    # ------------------------------------------------------------------
    # Inference logic (stub)
    # ------------------------------------------------------------------

    def _run_inference(self, payload: dict) -> dict:
        """Run model inference or fall back to heuristic."""
        if self.model is not None:
            return self._model_predict(payload)
        return self._heuristic_fallback(payload)

    def _model_predict(self, payload: dict) -> dict:
        """Delegate to the attached model.  STUB – not yet implemented."""
        raise NotImplementedError("Attach a model via self.model first.")

    def _heuristic_fallback(self, payload: dict) -> dict:
        """Simple heuristic used when no model is loaded."""
        return {
            "signal": "hold",
            "confidence": 0.0,
            "source": "heuristic_fallback",
            "input": payload,
        }

    # ------------------------------------------------------------------
    # Thread run loop (stub – override for continuous inference)
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Background loop placeholder.  STUB."""
        pass
