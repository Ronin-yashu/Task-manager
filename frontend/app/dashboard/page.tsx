"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Task, User } from "@/lib/types";
import TaskCard from "@/components/TaskCard";
import TaskForm from "@/components/TaskForm";

const VIEWS = [
  { key: "all", label: "All" },
  { key: "assigned", label: "Assigned to me" },
  { key: "created", label: "Created by me" },
];

const STATUSES = [
  { key: "all", label: "Any status" },
  { key: "pending", label: "Pending" },
  { key: "in_progress", label: "In progress" },
  { key: "completed", label: "Completed" },
];

export default function Dashboard() {
  const router = useRouter();
  const [me, setMe] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [view, setView] = useState("all");
  const [status, setStatus] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  const handleError = useCallback(
    (err: unknown) => {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/");
        return;
      }
      setError(err instanceof Error ? err.message : "Something went wrong");
    },
    [router]
  );

  const loadTasks = useCallback(async () => {
    try {
      setTasks(await api.tasks(view, status));
      setError("");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [view, status, handleError]);

  useEffect(() => {
    api.me().then(setMe).catch(handleError);
    api.users().then(setUsers).catch(handleError);
  }, [handleError]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  async function run(action: () => Promise<unknown>) {
    try {
      await action();
      await loadTasks();
    } catch (err) {
      handleError(err);
    }
  }

  async function logout() {
    await api.logout().catch(() => undefined);
    router.replace("/");
  }

  function handleDelete(id: string) {
    if (window.confirm("Delete this task?")) {
      run(() => api.deleteTask(id));
    }
  }

  function handleCreated() {
    setShowForm(false);
    loadTasks();
  }

  if (!me) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 text-gray-500">
        Loading...
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <h1 className="text-lg font-semibold">Task Manager</h1>
          <div className="flex items-center gap-3">
            {me.avatar_url && (
              <img
                src={me.avatar_url}
                alt=""
                referrerPolicy="no-referrer"
                className="h-8 w-8 rounded-full"
              />
            )}
            <span className="hidden text-sm text-gray-700 sm:inline">{me.name ?? me.email}</span>
            <button
              onClick={logout}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl space-y-5 px-4 py-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex gap-1 rounded-lg bg-gray-200 p-1">
            {VIEWS.map((item) => (
              <button
                key={item.key}
                onClick={() => setView(item.key)}
                className={`rounded-md px-3 py-1.5 text-sm ${
                  view === item.key ? "bg-white font-medium shadow-sm" : "text-gray-600"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900"
            >
              {STATUSES.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
            <button
              onClick={() => setShowForm((value) => !value)}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              New task
            </button>
          </div>
        </div>

        {showForm && (
          <TaskForm users={users} onCreated={handleCreated} onCancel={() => setShowForm(false)} />
        )}

        {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

        {loading ? (
          <p className="text-sm text-gray-500">Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <p className="rounded-xl border border-dashed border-gray-300 p-10 text-center text-sm text-gray-500">
            No tasks here yet.
          </p>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                me={me}
                onStart={(id) => run(() => api.startTask(id))}
                onComplete={(id) => run(() => api.completeTask(id))}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}