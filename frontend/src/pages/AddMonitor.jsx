import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createMonitor } from "../api/client.js";

const INITIAL_FORM = {
  name: "",
  url: "",
  interval_seconds: "60",
  expected_status_code: "200",
  timeout_seconds: "10",
  is_active: true,
};

export default function AddMonitor() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_FORM);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { checked, name, type, value } = event.target;
    setForm((currentForm) => ({
      ...currentForm,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    const validationError = validateForm(form);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      await createMonitor({
        name: form.name.trim(),
        url: form.url.trim(),
        interval_seconds: Number(form.interval_seconds),
        expected_status_code: Number(form.expected_status_code),
        timeout_seconds: Number(form.timeout_seconds),
        is_active: form.is_active,
      });
      setMessage("Monitor created");
      window.setTimeout(
        () =>
          navigate("/", {
            replace: true,
            state: { message: "Monitor created" },
          }),
        600,
      );
    } catch (err) {
      setError(err.message);
      setIsSubmitting(false);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Monitors</p>
          <h1>Add Monitor</h1>
        </div>
      </header>

      {error ? <div className="alert alert-error">{error}</div> : null}
      {message ? <div className="alert alert-success">{message}</div> : null}

      <form className="form-panel" onSubmit={handleSubmit} noValidate>
        <label>
          <span>Name</span>
          <input
            name="name"
            type="text"
            autoComplete="off"
            required
            value={form.name}
            onChange={handleChange}
          />
        </label>

        <label>
          <span>URL</span>
          <input
            name="url"
            type="url"
            autoComplete="off"
            required
            placeholder="https://example.com"
            value={form.url}
            onChange={handleChange}
          />
        </label>

        <div className="form-grid">
          <label>
            <span>Interval</span>
            <input
              name="interval_seconds"
              type="number"
              min="1"
              required
              value={form.interval_seconds}
              onChange={handleChange}
            />
          </label>

          <label>
            <span>Expected status</span>
            <input
              name="expected_status_code"
              type="number"
              min="100"
              max="599"
              required
              value={form.expected_status_code}
              onChange={handleChange}
            />
          </label>

          <label>
            <span>Timeout</span>
            <input
              name="timeout_seconds"
              type="number"
              min="1"
              required
              value={form.timeout_seconds}
              onChange={handleChange}
            />
          </label>
        </div>

        <label className="checkbox-row">
          <input
            name="is_active"
            type="checkbox"
            checked={form.is_active}
            onChange={handleChange}
          />
          <span>Active</span>
        </label>

        <div className="form-actions">
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving" : "Save Monitor"}
          </button>
        </div>
      </form>
    </section>
  );
}

function validateForm(form) {
  const requiredFields = [];

  if (!form.name.trim()) {
    requiredFields.push("Name");
  }

  if (!form.url.trim()) {
    requiredFields.push("URL");
  }

  if (!form.interval_seconds) {
    requiredFields.push("Interval");
  }

  if (!form.expected_status_code) {
    requiredFields.push("Expected status");
  }

  if (!form.timeout_seconds) {
    requiredFields.push("Timeout");
  }

  if (requiredFields.length > 0) {
    return `Fill required fields: ${requiredFields.join(", ")}`;
  }

  try {
    const url = new URL(form.url.trim());
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return "URL must start with http:// or https://";
    }
  } catch {
    return "URL must be valid";
  }

  const intervalSeconds = Number(form.interval_seconds);
  if (!Number.isInteger(intervalSeconds) || intervalSeconds < 1) {
    return "Interval must be a positive whole number";
  }

  const expectedStatusCode = Number(form.expected_status_code);
  if (
    !Number.isInteger(expectedStatusCode) ||
    expectedStatusCode < 100 ||
    expectedStatusCode > 599
  ) {
    return "Expected status must be between 100 and 599";
  }

  const timeoutSeconds = Number(form.timeout_seconds);
  if (!Number.isInteger(timeoutSeconds) || timeoutSeconds < 1) {
    return "Timeout must be a positive whole number";
  }

  return "";
}
