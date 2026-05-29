const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Общая обертка над fetch: добавляет JSON-заголовки и единый разбор ошибок.
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await readError(response);
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function readError(response) {
  // FastAPI обычно возвращает detail, но fallback нужен для любых HTTP-ошибок.
  try {
    const data = await response.json();
    return data.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

export function getHealth() {
  return request("/health");
}

export function getStats() {
  return request("/stats");
}

export function getMonitors() {
  return request("/monitors");
}

export function getMonitor(monitorId) {
  return request(`/monitors/${monitorId}`);
}

export function getMonitorChecks(monitorId) {
  return request(`/monitors/${monitorId}/checks`);
}

export function getMonitorIncidents(monitorId) {
  return request(`/monitors/${monitorId}/incidents`);
}

export function getIncidents(status) {
  const query = status && status !== "ALL" ? `?status=${status}` : "";
  return request(`/incidents${query}`);
}

export function createMonitor(payload) {
  return request("/monitors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateMonitor(monitorId, payload) {
  return request(`/monitors/${monitorId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function runMonitorCheck(monitorId) {
  return request(`/monitors/${monitorId}/check`, {
    method: "POST",
  });
}

export function deleteMonitor(monitorId) {
  return request(`/monitors/${monitorId}`, {
    method: "DELETE",
  });
}
