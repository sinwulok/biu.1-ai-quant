# REORG_NOTES.md

## Repository Reorganisation – March 2026

### Branch
`refactor/rename-agents-to-legacy-and-add-ai-skeleton`

### Created
2026-03-07

### Summary
The original rule-based agent code that lived in `backend/agents` has been
archived to `backend/legacy_rule_agents` via `git mv` (history is fully
preserved).  A new `backend/ai_agents` package has been added as the starting
point for model-driven agents.

### ⚠ Breaking Change (no-shim)
Any code that previously imported from `backend.agents` will now fail with an
`ImportError` because no compatibility shim has been added.  This is
intentional – the operator accepted a clean break.

### Files moved
All files previously under `backend/agents/` are now under
`backend/legacy_rule_agents/`:

- `__init__.py`
- `base_agent.py`
- `coordinator.py`
- `data_agent.py`
- `decision_agent.py`
- `execution_agent.py`
- `macd_agent.py`
- `risk_agent.py`

### New files added
| Path | Purpose |
|------|---------|
| `backend/ai_agents/__init__.py` | AI-first agents package stub |
| `backend/ai_agents/model_inference_agent.py` | Starter stub for model inference |
| `REORG_NOTES.md` | This file |
| `backend/legacy_rule_agents/README.md` | Archive notice and restore instructions |

### How to restore `backend/agents` (revert the move)

```bash
# 1. Ensure you are on the branch that contains this change.
git checkout refactor/rename-agents-to-legacy-and-add-ai-skeleton

# 2. Move the directory back.
git mv backend/legacy_rule_agents backend/agents

# 3. Commit the revert.
git commit -m "revert: restore backend/agents from legacy_rule_agents"
```

Alternatively, revert the entire commit that performed the move:

```bash
git revert <commit-sha-of-the-move>
```
