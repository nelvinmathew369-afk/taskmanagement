const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getAuthHeader() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });
    const isJson = res.headers.get("content-type")?.includes("application/json");
    const data = isJson ? await res.json() : await res.text();

    if (!res.ok) {
      const errorMsg = data?.message || data?.detail || res.statusText || "Request failed";
      const err = new Error(typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg));
      err.status = res.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  login: (username, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  getMe: () => request("/auth/me"),

  // Tasks
  getTasks: (params = {}) => {
    const query = new URLSearchParams();
    if (params.status) query.append("status", params.status);
    if (params.priority) query.append("priority", params.priority);
    if (params.search) query.append("search", params.search);
    const queryString = query.toString() ? `?${query.toString()}` : "";
    return request(`/tasks${queryString}`);
  },

  getTaskSummary: () => request("/tasks/summary"),

  getTaskById: (id) => request(`/tasks/${id}`),

  createTask: (taskData) =>
    request("/tasks", {
      method: "POST",
      body: JSON.stringify(taskData),
    }),

  updateTask: (id, updates) =>
    request(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    }),

  deleteTask: (id) =>
    request(`/tasks/${id}`, {
      method: "DELETE",
    }),

  // AI Extraction
  extractTaskAI: (text) =>
    request("/tasks/extract", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
};
