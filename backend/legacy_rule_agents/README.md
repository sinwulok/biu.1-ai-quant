# legacy_rule_agents

> **Archived snapshot** – this directory contains the rule-based agents that
> were previously located at `backend/agents`.  They have been moved here via
> `git mv` so full history is preserved.  No files have been modified during
> the move.

## Contents

| File | Description |
|------|-------------|
| `__init__.py` | Package init (agents export) |
| `base_agent.py` | Abstract `BaseAgent` thread-based base class |
| `coordinator.py` | Message-routing coordinator |
| `data_agent.py` | Market-data fetching agent |
| `decision_agent.py` | Rule-based trading decision agent |
| `execution_agent.py` | Order execution agent |
| `macd_agent.py` | MACD signal agent |
| `risk_agent.py` | Risk-management agent |

## Why this folder exists

As part of the AI-first refactor
(`refactor/rename-agents-to-legacy-and-add-ai-skeleton`), the original
rule-based agents were archived here.  New model-driven agents live in
`backend/ai_agents`.

## ⚠ Import path change (breaking, no-shim)

Imports must be updated from:

```python
from backend.agents import SomeAgent
```

to:

```python
from backend.legacy_rule_agents import SomeAgent  # archived rule-based agent
# -- or --
from backend.ai_agents import SomeAgent           # new AI-first agent
```

## How to restore `backend/agents`

If you need to revert this move:

```bash
git mv backend/legacy_rule_agents backend/agents
git commit -m "revert: restore backend/agents from legacy_rule_agents"
```
