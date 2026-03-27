# biu.1 AI Quant — HK Automated Trading Simulation Platform

一個模組化、可擴展的 AI 量化交易系統，以 **香港市場（HKEX）** 為主要目標，
整合 **IBKR**、**FUTU**、**CCXT** 及 **YFinance** 的全自動交易策略模擬平台。

> **This project is in active development. Do not use in live trading without full understanding and customisation.**

---

## 系統架構

![系統架構圖](public/x-biu-ai-quant-full-mmd.png)

---

## 主要功能

| 功能 | 說明 |
|------|------|
| **HK 市場數據** | 透過 YFinance 獲取港股 OHLCV 數據（支援 `.HK` 格式） |
| **加密貨幣數據** | 透過 CCXT 獲取 BTC/ETH 等加密資產行情 |
| **IBKR 券商** | 透過 ib_insync 連接 Interactive Brokers（TWS / IB Gateway） |
| **FUTU 券商** | 透過 futu-openapi 連接富途牛牛（OpenD） |
| **紙上交易** | 內建 PaperBroker，無需外部連接即可模擬交易 |
| **回測引擎** | 事件驅動回測，計算收益率、Sharpe Ratio、最大回撤 |
| **MACD 策略** | MACD 金叉/死叉訊號 |
| **RSI 策略** | RSI 超買/超賣反轉訊號 |
| **MACD + RSI** | 組合確認訊號 |
| **風險管理** | 波動率、Sharpe、最大回撤限制 |
| **React 前端** | 實時儀表板，包含價格圖表、組合、成交記錄 |

---

## 目錄結構

```
backend/
├── agents/           # 多代理框架
│   ├── base_agent.py
│   ├── coordinator.py
│   ├── data_agent.py      # YFinance 數據代理
│   ├── macd_agent.py      # MACD 策略代理
│   ├── decision_agent.py  # 決策代理
│   ├── execution_agent.py # 執行代理（委託 broker）
│   └── risk_agent.py      # 風險管理代理
├── brokers/          # 券商介面層
│   ├── base_broker.py     # 抽象基礎類別
│   ├── paper_broker.py    # 內建紙上交易（預設）
│   ├── ibkr_broker.py     # Interactive Brokers
│   ├── futu_broker.py     # 富途 (FUTU)
│   └── ccxt_broker.py     # CCXT（加密貨幣）
├── data/             # 數據來源
│   ├── yfinance_source.py # YFinance（港股 + 全球）
│   └── ccxt_source.py     # CCXT（加密貨幣）
├── simulation/       # 回測 / 模擬引擎
│   └── engine.py
├── utils/            # 技術指標與分析工具
│   ├── indicators.py      # MACD, RSI, Bollinger Bands
│   └── analysis.py        # 收益率、夏普比率等
├── api/
│   └── main.py            # FastAPI REST API
└── config.py              # 全域配置
frontend/
├── src/
│   ├── App.js
│   ├── components/
│   │   ├── Dashboard.js   # 主儀表板（圖表、組合、成交）
│   │   ├── ControlPanel.js # 系統控制、回測設定
│   │   ├── Portfolio.js
│   │   └── TradeHistory.js
└── package.json
```

---

## 配置

所有配置集中於 `backend/config.py`：

```python
# HK 股票清單
HK_DEFAULT_SYMBOLS = ["0700.HK", "0005.HK", ...]

# 啟用 IBKR（需先安裝並啟動 TWS）
IBKR_CONFIG = { "enabled": True, "port": 7497, ... }

# 啟用 FUTU（需先安裝並啟動 OpenD）
FUTU_CONFIG = { "enabled": True, "port": 11111, ... }

# 模擬參數
SIMULATION_CONFIG = {
    "initial_capital": 1_000_000.0,  # HKD
    "commission_rate": 0.0012,
    "stamp_duty_rate": 0.0013,
    ...
}
```

---

## API 端點

| Method | Endpoint | 說明 |
|--------|----------|------|
| `POST` | `/api/system/start` | 啟動系統（指定 broker、data source、symbols） |
| `POST` | `/api/system/stop` | 停止系統 |
| `GET`  | `/api/system/status` | 系統狀態 |
| `GET`  | `/api/market/symbols` | HK 預設股票清單 |
| `GET`  | `/api/market/crypto-symbols` | 加密貨幣清單 |
| `GET`  | `/api/market/price/{symbol}` | 最新股價 |
| `GET`  | `/api/market/ohlcv/{symbol}` | OHLCV 歷史數據 |
| `POST` | `/api/backtest/run` | 執行回測 |
| `GET`  | `/api/broker/list` | 可用券商列表及狀態 |
| `GET`  | `/api/trades` | 成交記錄 |
| `GET`  | `/api/portfolio` | 組合及現金 |

---

## 版本

`0.2.0` — HK 市場整合、IBKR / FUTU / CCXT 支援、回測引擎、React 儀表板
