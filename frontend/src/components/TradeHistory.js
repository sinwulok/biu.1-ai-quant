// src/components/TradeHistory.js
import React from "react";

export default function TradeHistory({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="card">
        <h2>Trade History</h2>
        <p style={{ color: "#8b949e", fontSize: "0.82rem" }}>No trades executed yet.</p>
      </div>
    );
  }

  const sorted = [...trades].reverse();

  return (
    <div className="card">
      <h2>Trade History <span style={{ color: "#8b949e", fontWeight: 400 }}>({trades.length})</span></h2>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Symbol</th>
              <th>Action</th>
              <th style={{ textAlign: "right" }}>Qty</th>
              <th style={{ textAlign: "right" }}>Price</th>
              <th>Status</th>
              <th>Broker</th>
            </tr>
          </thead>
          <tbody>
            {sorted.slice(0, 50).map((t, i) => (
              <tr key={i}>
                <td style={{ whiteSpace: "nowrap", color: "#8b949e", fontSize: "0.75rem" }}>
                  {t.fill_timestamp
                    ? new Date(t.fill_timestamp).toLocaleString()
                    : t.timestamp
                    ? new Date(t.timestamp).toLocaleString()
                    : "—"}
                </td>
                <td style={{ fontWeight: 600 }}>{t.symbol}</td>
                <td>
                  <span className={`badge ${t.action === "buy" ? "badge-green" : "badge-red"}`}>
                    {t.action?.toUpperCase()}
                  </span>
                </td>
                <td style={{ textAlign: "right" }}>{Number(t.filled_quantity || t.quantity || 0).toLocaleString()}</td>
                <td style={{ textAlign: "right" }}>
                  {t.filled_price != null ? Number(t.filled_price).toFixed(2) : "—"}
                </td>
                <td>
                  <span className={`badge ${t.status === "filled" ? "badge-green" : "badge-yellow"}`}>
                    {t.status}
                  </span>
                </td>
                <td style={{ color: "#8b949e", fontSize: "0.75rem" }}>{t.broker || "paper"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
