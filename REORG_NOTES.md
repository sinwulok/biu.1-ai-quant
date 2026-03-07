# Reorganisation Notes

**Date:** 2026-03-07  
**Branch:** `refactor/rename-agents-to-legacy-and-add-ai-skeleton`  
**Repository:** sinwulok/biu.1-ai-quant

---

## Summary

This refactor archives the original rule-based agents and lays the groundwork
for a new AI-first agent layer.

| Action | Old path | New path |
|--------|----------|----------|
| Rename (git mv) | `backend/agents/` | `backend/legacy_rule_agents/` |
| New skeleton | — | `backend/ai_agents/` |

---

## What was renamed

All files that lived under `backend/agents/` have been moved verbatim to
`backend/legacy_rule_agents/`.  No file contents were changed; only the
directory name changed.

Moved files:

- `backend/legacy_rule_agents/__init__.py`
- `backend/legacy_rule_agents/base_agent.py`
- `backend/legacy_rule_agents/coordinator.py`
- `backend/legacy_rule_agents/data_agent.py`
- `backend/legacy_rule_agents/decision_agent.py`
- `backend/legacy_rule_agents/execution_agent.py`
- `backend/legacy_rule_agents/macd_agent.py`
- `backend/legacy_rule_agents/risk_agent.py`

---

## What was added

New skeleton under `backend/ai_agents/`:

- `backend/ai_agents/__init__.py` — package docstring
- `backend/ai_agents/model_inference_agent.py` — starter stub implementing
  `ModelInferenceAgent` (inherits `BaseAgent`); includes heuristic fallback
  until a real model is supplied.

Documentation:

- `REORG_NOTES.md` (this file)
- `backend/legacy_rule_agents/README.md` — snapshot note and restore instructions

---

## Breaking changes

No import shim was added.  Any code that previously imported from
`backend.agents` will raise `ModuleNotFoundError` until updated to import
from `backend.legacy_rule_agents`.

### How to restore

If you need to roll back:

```bash
git mv backend/legacy_rule_agents backend/agents
git commit -m "revert: restore backend/agents"
```
