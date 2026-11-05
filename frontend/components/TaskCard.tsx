import { Priority, Status, Task, User } from "@/lib/types";

interface Props {
  task: Task;
  me: User;
  onStart: (id: string) => void;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
}

const PRIORITY_STYLES: Record<Priority, string> = {
  low: "bg-gray-100 text-gray-700",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-red-100 text-red-700",
};

const STATUS_STYLES: Record<Status, string> = {
  pending: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
};

const STATUS_LABELS: Record<Status, string> = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
};

function personLabel(person: User | null, me: User) {
  if (!person) return "Unassigned";
  if (person.id === me.id) return "You";
  return person.name ?? person.email;
}

export default function TaskCard({ task, me, onStart, onComplete, onDelete }: Props) {
  const today = new Date().toLocaleDateString("en-CA");
  const overdue =
    task.due_date !== null && task.due_date < today && task.status !== "completed";
  const isCreator = task.created_by === me.id;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3
            className={`text-base font-semibold ${
              task.status === "completed" ? "text-gray-400 line-through" : ""
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p className="mt-1 whitespace-pre-line text-sm text-gray-600">
              {task.description}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${PRIORITY_STYLES[task.priority]}`}>
            {task.priority}
          </span>
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[task.status]}`}>
            {STATUS_LABELS[task.status]}
          </span>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="text-xs text-gray-500">
          <span>From {personLabel(task.creator, me)}</span>
          <span className="mx-1.5">&rarr;</span>
          <span>{personLabel(task.assignee, me)}</span>
          {task.due_date && (
            <span className={`ml-3 ${overdue ? "font-medium text-red-600" : ""}`}>
              Due {task.due_date}
              {overdue && " (overdue)"}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          {task.status === "pending" && (
            <button
              onClick={() => onStart(task.id)}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
            >
              Start
            </button>
          )}
          {task.status !== "completed" && (
            <button
              onClick={() => onComplete(task.id)}
              className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
            >
              Mark complete
            </button>
          )}
          {isCreator && (
            <button
              onClick={() => onDelete(task.id)}
              className="rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}