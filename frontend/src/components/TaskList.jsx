import React from "react";
import { Edit2, Trash2, Calendar, AlertCircle } from "lucide-react";

export default function TaskList({
  tasks,
  loading,
  onEditTask,
  onDeleteTask,
  onStatusChange,
}) {
  const getStatusBadge = (status) => {
    switch (status) {
      case "Completed":
        return <span className="badge badge-completed">Completed</span>;
      case "In Progress":
        return <span className="badge badge-progress">In Progress</span>;
      default:
        return <span className="badge badge-pending">Pending</span>;
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case "High":
        return <span className="badge badge-high">High</span>;
      case "Low":
        return <span className="badge badge-low">Low</span>;
      default:
        return <span className="badge badge-medium">Medium</span>;
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "4rem 1rem", textAlign: "center", color: "#64748b" }}>
        <p>Loading tasks from database...</p>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div
        className="task-table-wrapper"
        style={{ padding: "4rem 2rem", textAlign: "center" }}
      >
        <div style={{ color: "#94a3b8", marginBottom: "0.5rem" }}>
          <AlertCircle size={36} style={{ margin: "0 auto" }} />
        </div>
        <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#334155" }}>
          No tasks found
        </h3>
        <p style={{ fontSize: "0.875rem", color: "#64748b", marginTop: "0.25rem" }}>
          No tasks match your filter criteria or the database is currently empty.
        </p>
      </div>
    );
  }

  return (
    <div className="task-table-wrapper">
      <table className="task-table">
        <thead>
          <tr>
            <th style={{ width: "70px" }}>ID</th>
            <th>Task Details</th>
            <th style={{ width: "120px" }}>Priority</th>
            <th style={{ width: "160px" }}>Status</th>
            <th style={{ width: "130px" }}>Due Date</th>
            <th style={{ width: "100px", textAlign: "right" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>
                <span style={{ fontWeight: 600, color: "#64748b" }}>#{task.id}</span>
              </td>
              <td>
                <div style={{ fontWeight: 600, color: "#0f172a", fontSize: "0.9375rem" }}>
                  {task.title}
                </div>
                {task.description && (
                  <div style={{ color: "#64748b", fontSize: "0.8125rem", marginTop: "0.2rem" }}>
                    {task.description}
                  </div>
                )}
                <div style={{ color: "#94a3b8", fontSize: "0.75rem", marginTop: "0.3rem" }}>
                  Created: {new Date(task.created_at).toLocaleDateString()}
                </div>
              </td>
              <td>{getPriorityBadge(task.priority)}</td>
              <td>
                <select
                  value={task.status}
                  onChange={(e) => onStatusChange(task.id, e.target.value)}
                  style={{
                    padding: "0.25rem 0.5rem",
                    borderRadius: "6px",
                    border: "1px solid #cbd5e1",
                    fontSize: "0.8125rem",
                    cursor: "pointer",
                    background: "white",
                  }}
                >
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                </select>
              </td>
              <td>
                {task.due_date ? (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "#334155" }}>
                    <Calendar size={14} style={{ color: "#64748b" }} />
                    <span>{task.due_date}</span>
                  </div>
                ) : (
                  <span style={{ color: "#94a3b8", fontSize: "0.8125rem" }}>None</span>
                )}
              </td>
              <td style={{ textAlign: "right" }}>
                <div style={{ display: "inline-flex", gap: "0.4rem" }}>
                  <button
                    className="btn btn-secondary"
                    style={{ padding: "0.35rem", borderRadius: "6px" }}
                    onClick={() => onEditTask(task)}
                    title="Edit task"
                  >
                    <Edit2 size={15} />
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ padding: "0.35rem", borderRadius: "6px", color: "#dc2626" }}
                    onClick={() => onDeleteTask(task.id)}
                    title="Delete task"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
