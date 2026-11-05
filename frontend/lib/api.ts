import { NewTask, Task, User } from "./types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(data?.error ?? "Request failed", response.status);
  }
  return data as T;
}

export const api = {
  me: () => request<User>("/auth/me"),
  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),
  users: () => request<User[]>("/users"),
  tasks: (view: string, status: string) => {
    const params = new URLSearchParams({ view });
    if (status !== "all") params.set("status", status);
    return request<Task[]>(`/tasks?${params.toString()}`);
  },
  createTask: (payload: NewTask) =>
    request<Task>("/tasks", { method: "POST", body: JSON.stringify(payload) }),
  startTask: (id: string) =>
    request<Task>(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "in_progress" }),
    }),
  completeTask: (id: string) =>
    request<Task>(`/tasks/${id}/complete`, { method: "POST" }),
  deleteTask: (id: string) =>
    request<{ message: string }>(`/tasks/${id}`, { method: "DELETE" }),
};