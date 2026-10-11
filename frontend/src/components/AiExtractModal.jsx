import React, { useState } from "react";
import { Sparkles, X, AlertCircle, CheckCircle, ArrowRight, Bot } from "lucide-react";
import { api } from "../api";

export default function AiExtractModal({ isOpen, onClose, onTaskCreated }) {
  const [instruction, setInstruction] = useState("");
  const [extracting, setExtracting] = useState(false);
  const [extractedResult, setExtractedResult] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const samplePrompts = [
    {
      label: "Assignment Example (Page 2)",
      text: "Prepare the monthly Ticket report by 15 October 2026. This is high priority.",
    },
    {
      label: "Missing Priority & Date",
      text: "Update system architecture documentation for Q4",
    },
    {
      label: "Ambiguous Date Warning",
      text: "Submit the financial audit tomorrow afternoon. This is urgent.",
    },
    {
      label: "Explicit Date & Low Priority",
      text: "Archive legacy server logs by 2026-12-31, low priority",
    },
  ];

  if (!isOpen) return null;

  const handleExtract = async () => {
    if (!instruction.trim()) {
      setError("Please enter a plain-English instruction to extract.");
      return;
    }

    setExtracting(true);
    setError("");
    setExtractedResult(null);

    try {
      const res = await api.extractTaskAI(instruction.trim());
      setExtractedResult(res);
    } catch (err) {
      setError(err.message || "Failed to extract task details.");
    } finally {
      setExtracting(false);
    }
  };

  const handleSaveToTasks = async () => {
    if (!extractedResult || !extractedResult.title) return;

    setSaving(true);
    setError("");

    try {
      const taskPayload = {
        title: extractedResult.title,
        description: extractedResult.description || null,
        priority: extractedResult.priority || "Medium",
        status: "Pending",
        due_date: extractedResult.due_date || null,
      };

      const created = await api.createTask(taskPayload);
      onTaskCreated(created);
      onClose();
    } catch (err) {
      setError(err.message || "Failed to save extracted task.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: "620px" }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">
            <Sparkles size={20} style={{ color: "#7c3aed" }} />
            <span>AI Task Extraction (Stage 2)</span>
          </h3>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <p style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "1rem" }}>
          Type a plain-English instruction. The AI extracts structured fields (Title, Priority, Due Date)
          for your review before submitting to <code>POST /tasks</code>.
        </p>

        {error && (
          <div className="error-banner">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="form-group">
          <label className="form-label">Plain-English Instruction</label>
          <textarea
            className="form-textarea"
            rows={3}
            placeholder="e.g. Prepare the monthly Ticket report by 15 October 2026. This is high priority."
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
          />
        </div>

        <div style={{ marginBottom: "1.25rem" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#64748b", marginBottom: "0.4rem" }}>
            Click sample to test:
          </div>
          <div className="chips-container">
            {samplePrompts.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="chip"
                onClick={() => {
                  setInstruction(sample.text);
                  setError("");
                }}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          className="btn btn-ai"
          style={{ width: "100%", padding: "0.7rem" }}
          onClick={handleExtract}
          disabled={extracting}
        >
          <Sparkles size={16} />
          <span>{extracting ? "Extracting with AI..." : "Extract Task Details"}</span>
        </button>

        {/* Extracted Details Preview Card */}
        {extractedResult && (
          <div className="ai-preview-box">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <h4 style={{ fontSize: "0.9375rem", fontWeight: 700, color: "#1e1b4b" }}>
                Extracted Task Preview
              </h4>
              <span className="ai-source-badge">
                <Bot size={13} />
                <span>{extractedResult.source}</span>
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "0.5rem", fontSize: "0.875rem" }}>
              <div>
                <strong style={{ color: "#475569" }}>Title:</strong>{" "}
                <span style={{ fontWeight: 600, color: "#0f172a" }}>{extractedResult.title}</span>
              </div>
              <div>
                <strong style={{ color: "#475569" }}>Priority:</strong>{" "}
                <span className={`badge badge-${extractedResult.priority.toLowerCase()}`}>
                  {extractedResult.priority}
                </span>
              </div>
              <div>
                <strong style={{ color: "#475569" }}>Due Date:</strong>{" "}
                <span>{extractedResult.due_date || "(None - not invented)"}</span>
              </div>
              {extractedResult.description && (
                <div>
                  <strong style={{ color: "#475569" }}>Description:</strong>{" "}
                  <span>{extractedResult.description}</span>
                </div>
              )}
            </div>

            {/* Clarification Alert if Date is Ambiguous */}
            {extractedResult.clarification_needed && (
              <div className="alert-warning">
                <AlertCircle size={16} />
                <span><strong>Clarification:</strong> {extractedResult.clarification_needed}</span>
              </div>
            )}

            <div style={{ marginTop: "1.25rem", display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSaveToTasks}
                disabled={saving}
              >
                <CheckCircle size={16} />
                <span>{saving ? "Saving to Database..." : "Confirm & Save Task (POST /tasks)"}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
