# legacy_rule_agents

This directory is a **snapshot** of the original `backend/agents/` package as it
existed before the refactor on 2026-03-07 (branch
`refactor/rename-agents-to-legacy-and-add-ai-skeleton`).

The files under `backend/agents/` have been preserved **without modification** at
the path:

```
backend/legacy_rule_agents/backend/agents/
```

## Contents

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `base_agent.py` | `BaseAgent` base class |
| `coordinator.py` | Agent coordinator / message bus |
| `data_agent.py` | Market-data fetching agent |
| `decision_agent.py` | Rule-based decision agent |
| `execution_agent.py` | Order execution agent |
| `macd_agent.py` | MACD signal agent |
| `risk_agent.py` | Risk management agent |

## How to restore

```bash
# From repo root
git mv backend/legacy_rule_agents/backend/agents backend/agents
rmdir backend/legacy_rule_agents/backend
rmdir backend/legacy_rule_agents
git commit -m "revert: restore backend/agents from legacy snapshot"
```
