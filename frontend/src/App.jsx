import React, { useState, useEffect, useCallback } from "react";
import Navbar from "./components/Navbar";
import LoginPage from "./components/LoginPage";
import TaskSummaryCards from "./components/TaskSummaryCards";
import TaskFilterBar from "./components/TaskFilterBar";
import TaskList from "./components/TaskList";
import TaskModal from "./components/TaskModal";
import AiExtractModal from "./components/AiExtractModal";
import { api } from "./api";

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  const [tasks, setTasks] = useState([]);
  const [summary, setSummary] = useState({ total: 0, pending: 0, in_progress: 0, completed: 0 });
  const [loading, setLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  // Modals
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);

  // Fetch summary
  const fetchSummary = useCallback(async () => {
    try {
      const data = await api.getTaskSummary();
      setSummary(data);
    } catch (err) {
      console.error("Failed to load task summary:", err);
    }
  }, []);

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getTasks({
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        search: search.trim() || undefined,
      });
      setTasks(data);
    } catch (err) {
      console.error("Failed to load tasks:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter, search]);

  // Load data when logged in
  useEffect(() => {
    if (user) {
      fetchTasks();
      fetchSummary();
    }
  }, [user, fetchTasks, fetchSummary]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const handleCreateNew = () => {
    setEditingTask(null);
    setIsTaskModalOpen(true);
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setIsTaskModalOpen(true);
  };

  const handleSaveTask = async (taskData) => {
    if (editingTask) {
      await api.updateTask(editingTask.id, taskData);
    } else {
      await api.createTask(taskData);
    }
    await fetchTasks();
    await fetchSummary();
  };

  const handleDeleteTask = async (id) => {
    if (window.confirm(`Are you sure you want to delete task #${id}?`)) {
      try {
        await api.deleteTask(id);
        await fetchTasks();
        await fetchSummary();
      } catch (err) {
        alert(err.message || "Failed to delete task.");
      }
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await api.updateTask(id, { status: newStatus });
      await fetchTasks();
      await fetchSummary();
    } catch (err) {
      alert(err.message || "Failed to update task status.");
    }
  };

  const handleTaskCreatedFromAi = async () => {
    await fetchTasks();
    await fetchSummary();
  };

  const handleFilterByStatus = (status) => {
    setStatusFilter((prev) => (prev === status ? "" : status));
  };

  if (!user) {
    return <LoginPage onLoginSuccess={setUser} />;
  }

  return (
    <div className="app-container">
      <Navbar user={user} onLogout={handleLogout} />

      <main className="main-content">
        {/* Stage 1: Summary Counts */}
        <TaskSummaryCards
          summary={summary}
          onFilterByStatus={handleFilterByStatus}
        />

        {/* Stage 1 & 2: Filters, Search, and Action Triggers */}
        <TaskFilterBar
          search={search}
          setSearch={setSearch}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          priorityFilter={priorityFilter}
          setPriorityFilter={setPriorityFilter}
          onOpenCreateModal={handleCreateNew}
          onOpenAiModal={() => setIsAiModalOpen(true)}
        />

        {/* Stage 1: Tasks List Table */}
        <TaskList
          tasks={tasks}
          loading={loading}
          onEditTask={handleEditTask}
          onDeleteTask={handleDeleteTask}
          onStatusChange={handleStatusChange}
        />
      </main>

      {/* Task Create / Edit Modal */}
      <TaskModal
        isOpen={isTaskModalOpen}
        onClose={() => {
          setIsTaskModalOpen(false);
          setEditingTask(null);
        }}
        onSubmit={handleSaveTask}
        initialData={editingTask}
      />

      {/* Stage 2: AI Task Extraction Modal */}
      <AiExtractModal
        isOpen={isAiModalOpen}
        onClose={() => setIsAiModalOpen(false)}
        onTaskCreated={handleTaskCreatedFromAi}
      />
    </div>
  );
}
