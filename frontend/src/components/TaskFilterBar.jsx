import React from "react";
import { Search, Plus, Sparkles, X } from "lucide-react";

export default function TaskFilterBar({
  search,
  setSearch,
  statusFilter,
  setStatusFilter,
  priorityFilter,
  setPriorityFilter,
  onOpenCreateModal,
  onOpenAiModal,
}) {
  return (
    <div className="control-bar">
      <div className="search-filter-group">
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="input-field"
            placeholder="Search tasks by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              style={{
                position: "absolute",
                right: "0.6rem",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "#94a3b8",
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        <select
          className="select-filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="Pending">Pending</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
        </select>

        <select
          className="select-filter"
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>
      </div>

      <div className="action-buttons-group">
        <button className="btn btn-ai" onClick={onOpenAiModal}>
          <Sparkles size={16} />
          <span>AI Task Extract</span>
        </button>

        <button className="btn btn-primary" onClick={onOpenCreateModal}>
          <Plus size={16} />
          <span>New Task</span>
        </button>
      </div>
    </div>
  );
}
