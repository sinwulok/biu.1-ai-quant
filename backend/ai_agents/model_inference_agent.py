"""
model_inference_agent.py — starter stub for the ModelInferenceAgent.

TODO: Replace the heuristic fallback with a real trained model.
"""

from backend.legacy_rule_agents.base_agent import BaseAgent


class ModelInferenceAgent(BaseAgent):
    """Stub agent that handles 'inference_request' messages.

    When a trained model is available it should be loaded in __init__ and
    called from _run_inference.  Until then a simple heuristic fallback is
    used so the rest of the system can be exercised end-to-end.
    """

    def __init__(self, name="model_inference_agent", model=None):
        super().__init__(name)
        self.model = model  # inject a trained model here when ready

    # ------------------------------------------------------------------
    # BaseAgent interface
    # ------------------------------------------------------------------

    def receive_message(self, message):
        if message.get("type") == "inference_request":
            payload = message.get("payload", {})
            result = self._run_inference(payload)
            self.send_message(
                target=message.get("sender"),
                message_type="inference_response",
                payload=result,
            )

    def run(self):
        # This agent is purely reactive (message-driven); nothing to poll.
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_inference(self, payload):
        """Return an inference result dict for *payload*.

        Uses the injected model when available; falls back to a simple
        heuristic (hold) otherwise.
        """
        if self.model is not None:
            # TODO: adapt to your model's actual input/output contract
            raw = self.model.predict(payload)
            return {"signal": raw, "source": "model"}

        # Heuristic fallback — always recommend 'hold'
        return {"signal": "hold", "source": "heuristic_fallback"}
