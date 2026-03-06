// src/components/Portfolio.js
import React from "react";

export default function Portfolio({ portfolio }) {
  const { cash = 0, positions = {}, broker = "paper" } = portfolio;
  const posEntries = Object.entries(positions);
  const total = cash; // simplified; real total would add position values

  return (
    <div className="card">
      <h2>
        Portfolio
        <span className="badge badge-blue" style={{ marginLeft: 8 }}>
          {broker}
        </span>
      </h2>

      <div className="metrics-row" style={{ marginBottom: 12 }}>
        <div className="metric-card">
          <div className="label">Cash</div>
          <div className="value">{cash.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
        </div>
        <div className="metric-card">
          <div className="label">Positions</div>
          <div className="value">{posEntries.length}</div>
        </div>
      </div>

      {posEntries.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th style={{ textAlign: "right" }}>Qty</th>
            </tr>
          </thead>
          <tbody>
            {posEntries.map(([sym, qty]) => (
              <tr key={sym}>
                <td>{sym}</td>
                <td style={{ textAlign: "right" }}>{Number(qty).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p style={{ color: "#8b949e", fontSize: "0.82rem" }}>No open positions.</p>
      )}
    </div>
  );
}
