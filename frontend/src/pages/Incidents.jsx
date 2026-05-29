import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getIncidents } from "../api/client.js";

const FILTERS = ["ALL", "OPEN", "RESOLVED"];

export default function Incidents() {
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [incidents, setIncidents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadIncidents = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      setIncidents(await getIncidents(activeFilter));
    } catch (err) {
      setError(err.message);
      setIncidents([]);
    } finally {
      setIsLoading(false);
    }
  }, [activeFilter]);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>Incidents</h1>
        </div>
        <div className="segmented-control" aria-label="Incident filter">
          {FILTERS.map((filter) => (
            <button
              className={filter === activeFilter ? "segment-active" : ""}
              key={filter}
              type="button"
              onClick={() => setActiveFilter(filter)}
              disabled={isLoading && filter === activeFilter}
            >
              {filter}
            </button>
          ))}
        </div>
      </header>

      {error ? <div className="alert alert-error">{error}</div> : null}

      <section className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Monitor</th>
                <th>Status</th>
                <th>Started</th>
                <th>Resolved</th>
                <th>Duration</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="6" className="empty-cell">
                    Loading
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-cell">
                    No incidents
                  </td>
                </tr>
              ) : (
                incidents.map((incident) => (
                  <tr key={incident.id}>
                    <td>{renderMonitor(incident)}</td>
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
                    <td>{incident.reason}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

function renderMonitor(incident) {
  if (!incident.monitor) {
    return `Monitor #${incident.monitor_id}`;
  }

  return (
    <Link to={`/monitors/${incident.monitor.id}`}>
      {incident.monitor.name || `Monitor #${incident.monitor.id}`}
    </Link>
  );
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
