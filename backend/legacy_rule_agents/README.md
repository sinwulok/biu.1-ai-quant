# legacy_rule_agents

This directory is a **snapshot** of the original `backend/agents/` package
as it existed before the AI-first refactor.  The files were moved here
unchanged using `git mv backend/agents backend/legacy_rule_agents`.

## Contents

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `base_agent.py` | Abstract `BaseAgent` base class |
| `coordinator.py` | Central message-routing coordinator |
| `data_agent.py` | Fetches market data on demand |
| `decision_agent.py` | Makes buy/sell/hold decisions from signals |
| `execution_agent.py` | Executes orders through the broker layer |
| `macd_agent.py` | MACD-based signal generator |
| `risk_agent.py` | Position-sizing and risk checks |

## Status

These agents are **archived**.  New development should target
`backend/ai_agents/`.

## Restore instructions

To restore the original directory name (e.g. to roll back the rename):

```bash
git mv backend/legacy_rule_agents backend/agents
git commit -m "revert: restore backend/agents directory name"
```

Then update any imports from `backend.legacy_rule_agents` back to
`backend.agents`.
