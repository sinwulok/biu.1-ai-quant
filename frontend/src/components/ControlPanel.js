// src/components/ControlPanel.js
import React, { useState } from "react";

const HK_SYMBOLS = [
  "0700.HK", "0005.HK", "0941.HK", "1299.HK", "0388.HK",
  "2318.HK", "0003.HK", "1398.HK", "0001.HK", "0016.HK",
];

const CRYPTO_SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT"];

const TIMEFRAME_OPTIONS = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk"];
const BACKTEST_PERIOD_OPTIONS = ["3mo", "6mo", "1y", "2y", "5y"];

export default function ControlPanel({ systemStatus, agents, onStart, onStop }) {
  const [broker, setBroker] = useState("paper");
  const [dataSource, setDataSource] = useState("yfinance");
  const [timeframe, setTimeframe] = useState("1d");
  const [selectedSymbols, setSelectedSymbols] = useState(["0700.HK", "0005.HK", "0941.HK"]);
  const [backtestResult, setBacktestResult] = useState(null);
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [strategy, setStrategy] = useState("macd");
  const [backtestPeriod, setBacktestPeriod] = useState("1y");

  const symbolList = dataSource === "ccxt" ? CRYPTO_SYMBOLS : HK_SYMBOLS;

  const toggleSymbol = (sym) => {
    setSelectedSymbols((prev) =>
      prev.includes(sym) ? prev.filter((s) => s !== sym) : [...prev, sym]
    );
  };

  const handleStart = () => {
    onStart({ broker, data_source: dataSource, timeframe, symbols: selectedSymbols });
  };

  const handleBacktest = async () => {
    setBacktestRunning(true);
    setBacktestResult(null);
    try {
      const res = await fetch("/api/backtest/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbols: selectedSymbols,
          data_source: dataSource,
          period: backtestPeriod,
          interval: timeframe,
          strategy,
        }),
      });
      const data = await res.json();
      setBacktestResult(data);
    } catch (e) {
      console.error("backtest error:", e);
    } finally {
      setBacktestRunning(false);
    }
  };

  return (
    <div>
      {/* --- System Control --- */}
      <div className="card">
        <h2>System Control</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button
            className="btn btn-primary"
            onClick={handleStart}
            disabled={systemStatus === "running"}
          >
            ▶ Start
          </button>
          <button
            className="btn btn-danger"
            onClick={onStop}
            disabled={systemStatus !== "running"}
          >
            ■ Stop
          </button>
        </div>

        {/* Agents */}
        {agents.length > 0 && (
          <div style={{ marginTop: 12 }}>
            {agents.map((a) => (
              <div key={a.name} style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: "0.8rem", color: "#8b949e" }}>{a.name}</span>
                <span className={`badge ${a.status === "running" ? "badge-green" : "badge-red"}`}>
                  {a.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* --- Configuration --- */}
      <div className="card">
        <h2>Configuration</h2>

        <label>Broker</label>
        <select value={broker} onChange={(e) => setBroker(e.target.value)}>
          <option value="paper">Paper (Built-in)</option>
          <option value="ibkr">IBKR (Interactive Brokers)</option>
          <option value="futu">FUTU (富途)</option>
          <option value="ccxt">CCXT (Crypto)</option>
        </select>

        <label>Data Source</label>
        <select value={dataSource} onChange={(e) => {
          setDataSource(e.target.value);
          setSelectedSymbols(e.target.value === "ccxt" ? ["BTC/USDT"] : ["0700.HK", "0005.HK"]);
        }}>
          <option value="yfinance">YFinance (HK &amp; Global)</option>
          <option value="ccxt">CCXT (Crypto)</option>
        </select>

        <label>Timeframe</label>
        <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
          {TIMEFRAME_OPTIONS.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* --- Symbol Selection --- */}
      <div className="card">
        <h2>Symbols</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {symbolList.map((sym) => (
            <button
              key={sym}
              className={`btn ${selectedSymbols.includes(sym) ? "btn-primary" : "btn-secondary"}`}
              style={{ padding: "4px 10px", fontSize: "0.75rem" }}
              onClick={() => toggleSymbol(sym)}
            >
              {sym}
            </button>
          ))}
        </div>
      </div>

      {/* --- Backtest --- */}
      <div className="card">
        <h2>Backtest</h2>

        <label>Strategy</label>
        <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
          <option value="macd">MACD Crossover</option>
          <option value="rsi">RSI Reversal</option>
          <option value="macd_rsi">MACD + RSI Combined</option>
        </select>

        <label>Period</label>
        <select value={backtestPeriod} onChange={(e) => setBacktestPeriod(e.target.value)}>
          {BACKTEST_PERIOD_OPTIONS.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>

        <div style={{ marginTop: 10 }}>
          <button
            className="btn btn-secondary"
            onClick={handleBacktest}
            disabled={backtestRunning || selectedSymbols.length === 0}
          >
            {backtestRunning ? "Running…" : "▶ Run Backtest"}
          </button>
        </div>

        {backtestResult && (
          <div style={{ marginTop: 12 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {[
                { label: "Return", value: `${backtestResult.total_return_pct}%`, positive: backtestResult.total_return_pct >= 0 },
                { label: "Sharpe",  value: backtestResult.sharpe_ratio },
                { label: "Max DD",  value: `${backtestResult.max_drawdown_pct}%`, positive: false },
                { label: "Trades",  value: backtestResult.num_trades },
              ].map((m) => (
                <div key={m.label} className="metric-card" style={{ padding: 8 }}>
                  <div className="label" style={{ fontSize: "0.68rem" }}>{m.label}</div>
                  <div className={`value ${m.positive === undefined ? "" : m.positive ? "positive" : "negative"}`}
                       style={{ fontSize: "1rem" }}>
                    {m.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
