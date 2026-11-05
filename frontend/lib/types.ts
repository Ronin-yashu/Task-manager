export type Status = "pending" | "in_progress" | "completed";
export type Priority = "low" | "medium" | "high";

export interface User {
  id: string;
  name: string | null;
  email: string;
  avatar_url: string | null;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: Status;
  priority: Priority;
  due_date: string | null;
  created_by: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  creator: User;
  assignee: User | null;
}

export interface NewTask {
  title: string;
  description: string | null;
  priority: Priority;
  due_date: string | null;
  assigned_to: string | null;
}