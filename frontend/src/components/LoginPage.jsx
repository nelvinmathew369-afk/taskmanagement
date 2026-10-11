import React, { useState } from "react";
import { CheckSquare, AlertCircle, ArrowRight, KeyRound } from "lucide-react";
import { api } from "../api";

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await api.login(username, password);
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || "Invalid username or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = () => {
    setUsername("admin");
    setPassword("admin123");
    setError("");
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">
            <CheckSquare size={28} />
          </div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, color: "#1e1b4b" }}>
            Sign In to TaskFlow AI
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b", marginTop: "0.25rem" }}>
            ERP AI Assistant Task Management System
          </p>
        </div>

        {error && (
          <div className="error-banner">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. admin"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", padding: "0.75rem", marginTop: "0.5rem" }}
            disabled={loading}
          >
            {loading ? "Authenticating..." : "Sign In to Task Section"}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        <div style={{ marginTop: "1.5rem", paddingTop: "1.25rem", borderTop: "1px solid #e2e8f0" }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ width: "100%", fontSize: "0.8125rem", gap: "0.4rem" }}
            onClick={handleQuickDemo}
          >
            <KeyRound size={15} />
            <span>Fill Demo Credentials (admin / admin123)</span>
          </button>
        </div>
      </div>
    </div>
  );
}
