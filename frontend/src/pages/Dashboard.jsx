import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import {
  deleteMonitor,
  getMonitorChecks,
  getMonitors,
  getStats,
  runMonitorCheck,
  updateMonitor,
} from "../api/client.js";

const EMPTY_STATS = {
  total_monitors: 0,
  up_monitors: 0,
  down_monitors: 0,
  unknown_monitors: 0,
  active_incidents: 0,
  average_latency_ms: null,
};

export default function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const [stats, setStats] = useState(EMPTY_STATS);
  const [monitors, setMonitors] = useState([]);
  const [latestChecks, setLatestChecks] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyAction, setBusyAction] = useState("");

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const [statsData, monitorData] = await Promise.all([
        getStats(),
        getMonitors(),
      ]);
      setStats(statsData);
      setMonitors(monitorData);
      setLatestChecks(await loadLatestChecks(monitorData));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const routeMessage = location.state?.message;
    if (!routeMessage) {
      return;
    }

    setMessage(routeMessage);
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  const statItems = useMemo(
    () => [
      { label: "Total monitors", value: stats.total_monitors },
      { label: "UP", value: stats.up_monitors },
      { label: "DOWN", value: stats.down_monitors },
      { label: "UNKNOWN", value: stats.unknown_monitors },
      { label: "Active incidents", value: stats.active_incidents },
      {
        label: "Average latency",
        value: formatLatency(stats.average_latency_ms),
      },
    ],
    [stats],
  );

  async function handleRunCheck(monitorId) {
    await runAction(`check-${monitorId}`, async () => {
      await runMonitorCheck(monitorId);
      setMessage("Check completed");
      await loadDashboard();
    });
  }

  async function handleToggleActive(monitor) {
    await runAction(`toggle-${monitor.id}`, async () => {
      await updateMonitor(monitor.id, { is_active: !monitor.is_active });
      setMessage(monitor.is_active ? "Monitor disabled" : "Monitor enabled");
      await loadDashboard();
    });
  }

  async function handleDelete(monitorId) {
    await runAction(`delete-${monitorId}`, async () => {
      await deleteMonitor(monitorId);
      setMessage("Monitor deleted");
      await loadDashboard();
    });
  }

  async function runAction(actionId, action) {
    setBusyAction(actionId);
    setError("");
    setMessage("");

    try {
      await action();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyAction("");
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Monitoring</p>
          <h1>Dashboard</h1>
        </div>
        <button type="button" onClick={loadDashboard} disabled={isLoading}>
          Refresh
        </button>
      </header>

      <div className="alert alert-success">
        Demo text for Railway deployment check. Remove this line during defense.
      </div>

      {error ? <div className="alert alert-error">{error}</div> : null}
      {message ? <div className="alert alert-success">{message}</div> : null}

      <div className="stats-grid">
        {statItems.map((item) => (
          <article className="stat-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      <section className="panel">
        <div className="panel-header">
          <h2>Monitors</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>URL</th>
                <th>Status</th>
                <th>Last checked</th>
                <th>Latency</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="6" className="empty-cell">
                    Loading
                  </td>
                </tr>
              ) : monitors.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-cell">
                    No monitors
                  </td>
                </tr>
              ) : (
                monitors.map((monitor) => {
                  const latestCheck = latestChecks[monitor.id];
                  return (
                    <tr key={monitor.id}>
                      <td>
                        <strong>{monitor.name}</strong>
                      </td>
                      <td>
                        <a href={monitor.url} target="_blank" rel="noreferrer">
                          {monitor.url}
                        </a>
                      </td>
                      <td>
                        <span
                          className={`status-pill status-${monitor.current_status.toLowerCase()}`}
                        >
                          {monitor.current_status}
                        </span>
                      </td>
                      <td>{formatDate(monitor.last_checked_at)}</td>
                      <td>{formatLatency(latestCheck?.latency_ms)}</td>
                      <td>
                        <div className="row-actions">
                          <Link className="text-button" to={`/monitors/${monitor.id}`}>
                            View
                          </Link>
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => handleRunCheck(monitor.id)}
                            disabled={busyAction === `check-${monitor.id}`}
                          >
                            Check
                          </button>
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() => handleToggleActive(monitor)}
                            disabled={busyAction === `toggle-${monitor.id}`}
                          >
                            {monitor.is_active ? "Disable" : "Enable"}
                          </button>
                          <button
                            type="button"
                            className="danger-button"
                            onClick={() => handleDelete(monitor.id)}
                            disabled={busyAction === `delete-${monitor.id}`}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

async function loadLatestChecks(monitors) {
  const checkEntries = await Promise.all(
    monitors.map(async (monitor) => {
      try {
        const checks = await getMonitorChecks(monitor.id);
        return [monitor.id, checks[0] ?? null];
      } catch {
        return [monitor.id, null];
      }
    }),
  );

  return Object.fromEntries(checkEntries);
}

function formatLatency(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  return `${Math.round(value)} ms`;
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
