// src/components/Dashboard.js
import React, { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import Portfolio from "./Portfolio";
import TradeHistory from "./TradeHistory";

const METRIC_CARDS = [
  { key: "total_return_pct", label: "Return (%)", suffix: "%" },
  { key: "sharpe_ratio",     label: "Sharpe Ratio" },
  { key: "max_drawdown_pct", label: "Max Drawdown (%)", suffix: "%" },
  { key: "num_trades",       label: "Trades" },
];

export default function Dashboard({ trades, portfolio, simulation }) {
  const [ohlcv, setOhlcv]     = useState([]);
  const [activeSymbol, setActiveSymbol] = useState("0700.HK");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/api/market/ohlcv/${encodeURIComponent(activeSymbol)}?period=3mo&interval=1d`);
        if (!res.ok) return;
        const { data } = await res.json();
        setOhlcv(data || []);
      } catch (err) {
        console.error("OHLCV fetch error:", err);
      }    };
    load();
  }, [activeSymbol]);

  const hkSymbols = ["0700.HK", "0005.HK", "0941.HK", "1299.HK", "0388.HK"];

  return (
    <div>
      {/* Summary metrics (from last backtest or simulation) */}
      {simulation && (
        <div className="metrics-row">
          {METRIC_CARDS.map((m) => {
            const val = simulation[m.key];
            const isReturn = m.key === "total_return_pct" || m.key === "max_drawdown_pct";
            const positive = isReturn ? val >= 0 : undefined;
            return (
              <div key={m.key} className="metric-card">
                <div className="label">{m.label}</div>
                <div className={`value ${positive === undefined ? "" : positive ? "positive" : "negative"}`}>
                  {val != null ? `${val}` : "—"}
                  {m.suffix && val != null ? m.suffix : ""}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Price Chart */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <h2 style={{ margin: 0, border: "none", padding: 0 }}>Price Chart</h2>
          <div style={{ display: "flex", gap: 6 }}>
            {hkSymbols.map((s) => (
              <button
                key={s}
                className={`btn ${s === activeSymbol ? "btn-primary" : "btn-secondary"}`}
                style={{ padding: "3px 8px", fontSize: "0.72rem" }}
                onClick={() => setActiveSymbol(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {ohlcv.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={ohlcv} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: "#8b949e" }}
                tickFormatter={(v) => v?.slice(5, 10)}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#8b949e" }}
                domain={["auto", "auto"]}
                width={55}
              />
              <Tooltip
                contentStyle={{ background: "#161b22", border: "1px solid #30363d", fontSize: 12 }}
                formatter={(v) => [Number(v).toFixed(2), "Close"]}
                labelFormatter={(l) => l?.slice(0, 10)}
              />
              <Line
                type="monotone"
                dataKey="Close"
                stroke="#58a6ff"
                dot={false}
                strokeWidth={1.5}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: "#8b949e", fontSize: "0.82rem" }}>Loading chart data…</p>
        )}
      </div>

      {/* Portfolio & Trade History */}
      <Portfolio portfolio={portfolio} />
      <TradeHistory trades={trades} />
    </div>
  );
}
