# REORG NOTES

**Date:** 2026-03-07  
**Branch:** `refactor/rename-agents-to-legacy-and-add-ai-skeleton`  
**Repository:** `sinwulok/biu.1-ai-quant`

## What changed

| Action | Path |
|--------|------|
| Moved (git mv) | `backend/agents/` → `backend/legacy_rule_agents/backend/agents/` |
| Added | `backend/ai_agents/__init__.py` |
| Added | `backend/ai_agents/model_inference_agent.py` |
| Added | `REORG_NOTES.md` (this file) |
| Added | `legacy_rule_agents/README.md` |

## Why

The original rule-based agents under `backend/agents/` are being preserved as a
historical snapshot while a new AI-first agent layer is introduced under
`backend/ai_agents/`.  This is an **intentional breaking change** — no shims or
backward-compatibility wrappers have been added.  Callers that previously imported
from `backend.agents` must update their import paths.

## Restore instructions

If you need to revert the move and restore `backend/agents/` to its original
location:

```bash
# From repo root
git mv backend/legacy_rule_agents/backend/agents backend/agents
rmdir backend/legacy_rule_agents/backend
rmdir backend/legacy_rule_agents
git commit -m "revert: restore backend/agents from legacy snapshot"
```
