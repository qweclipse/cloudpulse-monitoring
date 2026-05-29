import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  getMonitor,
  getMonitorChecks,
  getMonitorIncidents,
  runMonitorCheck,
} from "../api/client.js";

export default function MonitorDetails() {
  const { monitorId } = useParams();
  const [monitor, setMonitor] = useState(null);
  const [checks, setChecks] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadDetails = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const [monitorData, checkData, incidentData] = await Promise.all([
        getMonitor(monitorId),
        getMonitorChecks(monitorId),
        getMonitorIncidents(monitorId),
      ]);
      setMonitor(monitorData);
      setChecks(checkData);
      setIncidents(incidentData);
    } catch (err) {
      setMonitor(null);
      setChecks([]);
      setIncidents([]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [monitorId]);

  useEffect(() => {
    loadDetails();
  }, [loadDetails]);

  const uptimePercentage = useMemo(() => calculateUptime(checks), [checks]);

  async function handleRunCheck() {
    setIsChecking(true);
    setError("");
    setMessage("");

    try {
      await runMonitorCheck(monitorId);
      setMessage("Check completed");
      await loadDetails();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsChecking(false);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Monitor</p>
          <h1>{monitor?.name ?? `Monitor #${monitorId}`}</h1>
        </div>
        <div className="row-actions">
          <Link className="text-button" to="/">
            Dashboard
          </Link>
          <button
            type="button"
            onClick={handleRunCheck}
            disabled={isLoading || isChecking}
          >
            {isChecking ? "Checking" : "Run Check"}
          </button>
        </div>
      </header>

      {error ? <div className="alert alert-error">{error}</div> : null}
      {message ? <div className="alert alert-success">{message}</div> : null}

      <section className="details-grid">
        <article className="panel">
          <div className="panel-header">
            <h2>Status</h2>
          </div>
          {isLoading ? (
            <div className="empty-state">Loading</div>
          ) : monitor ? (
            <dl className="definition-list">
              <div>
                <dt>Current status</dt>
                <dd>
                  <span
                    className={`status-pill status-${monitor.current_status.toLowerCase()}`}
                  >
                    {monitor.current_status}
                  </span>
                </dd>
              </div>
              <div>
                <dt>URL</dt>
                <dd>
                  <a href={monitor.url} target="_blank" rel="noreferrer">
                    {monitor.url}
                  </a>
                </dd>
              </div>
              <div>
                <dt>Expected status</dt>
                <dd>{monitor.expected_status_code}</dd>
              </div>
              <div>
                <dt>Interval</dt>
                <dd>{monitor.interval_seconds} sec</dd>
              </div>
              <div>
                <dt>Timeout</dt>
                <dd>{monitor.timeout_seconds} sec</dd>
              </div>
              <div>
                <dt>Last checked</dt>
                <dd>{formatDate(monitor.last_checked_at)}</dd>
              </div>
              <div>
                <dt>Uptime</dt>
                <dd>{uptimePercentage}</dd>
              </div>
            </dl>
          ) : (
            <div className="empty-state">Monitor not found</div>
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2>Recent Checks</h2>
          </div>
          <div className="table-wrap">
            <table className="compact-table">
              <thead>
                <tr>
                  <th>Checked at</th>
                  <th>Result</th>
                  <th>Status code</th>
                  <th>Latency</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan="5" className="empty-cell">
                      Loading
                    </td>
                  </tr>
                ) : checks.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="empty-cell">
                      No checks
                    </td>
                  </tr>
                ) : (
                  checks.map((check) => (
                    <tr key={check.id}>
                      <td>{formatDate(check.checked_at)}</td>
                      <td>
                        <span
                          className={`status-pill status-${check.status.toLowerCase()}`}
                        >
                          {check.status}
                        </span>
                      </td>
                      <td>{check.status_code ?? "-"}</td>
                      <td>{formatLatency(check.latency_ms)}</td>
                      <td>{check.error_message ?? "-"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel details-wide">
          <div className="panel-header">
            <h2>Incidents</h2>
          </div>
          <div className="table-wrap">
            <table className="compact-table">
              <thead>
                <tr>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Resolved</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan="5" className="empty-cell">
                      Loading
                    </td>
                  </tr>
                ) : incidents.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="empty-cell">
                      No incidents
                    </td>
                  </tr>
                ) : (
                  incidents.map((incident) => (
                    <tr key={incident.id}>
                      <td>{incident.reason}</td>
                      <td>
                        <span
                          className={`status-pill status-${incident.status.toLowerCase()}`}
                        >
                          {incident.status}
                        </span>
                      </td>
                      <td>{formatDate(incident.started_at)}</td>
                      <td>{formatDate(incident.resolved_at)}</td>
                      <td>{formatDuration(incident.duration_seconds)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </section>
  );
}

function calculateUptime(checks) {
  if (checks.length === 0) {
    return "-";
  }

  const successCount = checks.filter(
    (check) => check.status === "SUCCESS",
  ).length;
  return `${((successCount / checks.length) * 100).toFixed(1)}%`;
}

function formatLatency(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  return `${Math.round(value)} ms`;
}

function formatDuration(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  return `${Math.round(value)} sec`;
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
