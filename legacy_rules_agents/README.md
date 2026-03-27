# Legacy Rules-Based Agents

This directory contains an archived copy of the original rules-based agent
implementations from `backend/agents/`.  The originals remain in place and
are still the active code; this folder serves as an easy-to-find snapshot of
the rules-based baseline before AI-driven agents are introduced.

## Contents

```
legacy_rules_agents/
└── backend/
    └── agents/
        ├── __init__.py          # Package init (exports all agents)
        ├── base_agent.py        # BaseAgent thread wrapper
        ├── coordinator.py       # AgentCoordinator message bus
        ├── data_agent.py        # Market data fetching (yfinance / CCXT)
        ├── macd_agent.py        # MACD crossover strategy
        ├── decision_agent.py    # Signal aggregation & order routing
        ├── execution_agent.py   # Broker-adapter order execution
        └── risk_agent.py        # Volatility / Sharpe risk checks
```

## How to restore files

If you ever need to restore any of these files to the live `backend/agents/`
directory, simply copy the relevant file:

```bash
cp legacy_rules_agents/backend/agents/<file>.py backend/agents/<file>.py
```

## Why this exists

As the project transitions toward AI-based strategies (see
`backend/agents/ai_agents/`), keeping the legacy rules-based logic archived
here makes it easy to compare, reference, or roll back without needing to dig
through git history.
