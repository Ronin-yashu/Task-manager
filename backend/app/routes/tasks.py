import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, g, jsonify
from ..db import supabase
from ..utils import login_required

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

TASK_SELECT = (
    "*, "
    "creator:users!tasks_created_by_fkey(id,name,email,avatar_url), "
    "assignee:users!tasks_assigned_to_fkey(id,name,email,avatar_url)"
)
STATUSES = {"pending", "in_progress", "completed"}
PRIORITIES = {"low", "medium", "high"}
EDITABLE_FIELDS = {"title", "description", "priority", "due_date", "assigned_to"}


def is_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def user_exists(user_id):
    if not is_uuid(user_id):
        return False
    result = supabase.table("users").select("id").eq("id", user_id).limit(1).execute()
    return bool(result.data)


def fetch_task(task_id):
    if not is_uuid(task_id):
        return None
    result = (
        supabase.table("tasks")
        .select(TASK_SELECT)
        .eq("id", task_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def has_access(task):
    user_id = g.user["id"]
    return user_id in (task["created_by"], task["assigned_to"])


def error(message, status):
    return jsonify({"error": message}), status


@bp.post("")
@login_required
def create_task():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    if not title or len(title) > 200:
        return error("Title is required and must be at most 200 characters", 400)

    priority = data.get("priority", "medium")
    if priority not in PRIORITIES:
        return error("Invalid priority", 400)

    assigned_to = data.get("assigned_to") or None
    if assigned_to and not user_exists(assigned_to):
        return error("Assignee not found", 400)

    row = {
        "title": title,
        "description": data.get("description"),
        "priority": priority,
        "due_date": data.get("due_date") or None,
        "created_by": g.user["id"],
        "assigned_to": assigned_to,
    }
    inserted = supabase.table("tasks").insert(row).execute()
    task = fetch_task(inserted.data[0]["id"])
    return jsonify(task), 201


@bp.get("")
@login_required
def list_tasks():
    view = request.args.get("view", "all")
    status = request.args.get("status")
    user_id = g.user["id"]

    query = supabase.table("tasks").select(TASK_SELECT)
    if view == "assigned":
        query = query.eq("assigned_to", user_id)
    elif view == "created":
        query = query.eq("created_by", user_id)
    else:
        query = query.or_(f"created_by.eq.{user_id},assigned_to.eq.{user_id}")

    if status in STATUSES:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).execute()
    return jsonify(result.data)


@bp.get("/<task_id>")
@login_required
def get_task(task_id):
    task = fetch_task(task_id)
    if not task:
        return error("Task not found", 404)
    if not has_access(task):
        return error("Forbidden", 403)
    return jsonify(task)


@bp.patch("/<task_id>")
@login_required
def update_task(task_id):
    task = fetch_task(task_id)
    if not task:
        return error("Task not found", 404)
    if not has_access(task):
        return error("Forbidden", 403)

    data = request.get_json(silent=True) or {}
    is_creator = task["created_by"] == g.user["id"]
    updates = {}

    edited_fields = EDITABLE_FIELDS & data.keys()
    if edited_fields and not is_creator:
        return error("Only the creator can edit task details", 403)

    if "title" in edited_fields:
        title = (data["title"] or "").strip()
        if not title or len(title) > 200:
            return error("Title is required and must be at most 200 characters", 400)
        updates["title"] = title

    if "description" in edited_fields:
        updates["description"] = data["description"]

    if "priority" in edited_fields:
        if data["priority"] not in PRIORITIES:
            return error("Invalid priority", 400)
        updates["priority"] = data["priority"]

    if "due_date" in edited_fields:
        updates["due_date"] = data["due_date"] or None

    if "assigned_to" in edited_fields:
        new_assignee = data["assigned_to"] or None
        if new_assignee and not user_exists(new_assignee):
            return error("Assignee not found", 400)
        updates["assigned_to"] = new_assignee

    if "status" in data:
        if data["status"] not in {"pending", "in_progress"}:
            return error("Use the complete endpoint to complete a task", 400)
        updates["status"] = data["status"]
        updates["completed_at"] = None

    if not updates:
        return error("Nothing to update", 400)

    supabase.table("tasks").update(updates).eq("id", task_id).execute()
    return jsonify(fetch_task(task_id))


@bp.post("/<task_id>/complete")
@login_required
def complete_task(task_id):
    task = fetch_task(task_id)
    if not task:
        return error("Task not found", 404)
    if not has_access(task):
        return error("Forbidden", 403)
    if task["status"] == "completed":
        return error("Task is already completed", 409)

    supabase.table("tasks").update(
        {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", task_id).execute()
    return jsonify(fetch_task(task_id))


@bp.delete("/<task_id>")
@login_required
def delete_task(task_id):
    task = fetch_task(task_id)
    if not task:
        return error("Task not found", 404)
    if task["created_by"] != g.user["id"]:
        return error("Only the creator can delete a task", 403)

    supabase.table("tasks").delete().eq("id", task_id).execute()
    return jsonify({"message": "Task deleted"})