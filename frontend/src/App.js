// src/App.js
import React, { useState, useEffect, useCallback } from "react";
import Dashboard from "./components/Dashboard";
import ControlPanel from "./components/ControlPanel";
import "./App.css";

const POLL_INTERVAL_MS = 5000;

function App() {
  const [systemStatus, setSystemStatus] = useState("stopped");
  const [agents, setAgents] = useState([]);
  const [trades, setTrades] = useState([]);
  const [portfolio, setPortfolio] = useState({});
  const [simulation, setSimulation] = useState(null);

  // ---- data fetchers ----
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/system/status");
      const data = await res.json();
      setSystemStatus(data.status);
      setAgents(data.agents || []);
      if (data.simulation) setSimulation(data.simulation);
    } catch (e) {
      console.error("fetchStatus:", e);
    }
  }, []);

  const fetchTrades = useCallback(async () => {
    try {
      const res = await fetch("/api/trades");
      setTrades(await res.json());
    } catch (e) {
      console.error("fetchTrades:", e);
    }
  }, []);

  const fetchPortfolio = useCallback(async () => {
    try {
      const res = await fetch("/api/portfolio");
      setPortfolio(await res.json());
    } catch (e) {
      console.error("fetchPortfolio:", e);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const id = setInterval(fetchStatus, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchStatus]);

  useEffect(() => {
    fetchTrades();
    fetchPortfolio();
    const id = setInterval(() => {
      fetchTrades();
      fetchPortfolio();
    }, POLL_INTERVAL_MS * 2);
    return () => clearInterval(id);
  }, [fetchTrades, fetchPortfolio]);

  // ---- system control ----
  const handleStart = async (config) => {
    try {
      const res = await fetch("/api/system/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (e) {
      console.error("handleStart:", e);
    }
  };

  const handleStop = async () => {
    try {
      const res = await fetch("/api/system/stop", { method: "POST" });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (e) {
      console.error("handleStop:", e);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h1>🤖 biu.1 AI Quant</h1>
          <div className="subtitle">HK Trading Simulation Platform · IBKR · FUTU · CCXT · YFinance</div>
        </div>
        <div className="system-status">
          System:{" "}
          <span className={`status-${systemStatus}`}>{systemStatus.toUpperCase()}</span>
        </div>
      </header>

      <main>
        <aside className="sidebar">
          <ControlPanel
            systemStatus={systemStatus}
            agents={agents}
            onStart={handleStart}
            onStop={handleStop}
          />
        </aside>

        <div className="content">
          <Dashboard
            trades={trades}
            portfolio={portfolio}
            simulation={simulation}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
