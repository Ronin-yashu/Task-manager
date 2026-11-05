import base64
import logging
import threading
from email.message import EmailMessage
from html import escape
import requests
from .config import Config

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def get_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": Config.GOOGLE_CLIENT_ID,
            "client_secret": Config.GOOGLE_CLIENT_SECRET,
            "refresh_token": Config.GMAIL_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def send_email(to, subject, html, text):
    message = EmailMessage()
    message["To"] = to
    message["From"] = Config.GMAIL_SENDER_EMAIL
    message["Subject"] = subject
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    response = requests.post(
        SEND_URL,
        headers={"Authorization": f"Bearer {get_access_token()}"},
        json={"raw": raw},
        timeout=10,
    )
    response.raise_for_status()


def send_async(to, subject, html, text):
    if not Config.GMAIL_SENDER_EMAIL or not Config.GMAIL_REFRESH_TOKEN:
        logger.warning("Gmail is not configured, skipping email to %s", to)
        return

    def run():
        try:
            send_email(to, subject, html, text)
        except Exception:
            logger.exception("Failed to send email to %s", to)

    threading.Thread(target=run, daemon=True).start()


def render(heading, intro, task):
    due = task.get("due_date") or "No due date"
    assignee = task["assignee"]["name"] if task.get("assignee") else "Unassigned"
    description = task.get("description") or ""
    link = f"{Config.FRONTEND_URL}/dashboard"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:8px">
      <h2 style="margin:0 0 8px">{escape(heading)}</h2>
      <p style="color:#4b5563">{escape(intro)}</p>
      <div style="background:#f9fafb;padding:16px;border-radius:6px">
        <p style="margin:0 0 8px;font-size:18px"><strong>{escape(task["title"])}</strong></p>
        <p style="margin:0 0 8px;color:#4b5563">{escape(description)}</p>
        <p style="margin:0;color:#6b7280;font-size:14px">
          Priority: {escape(task["priority"])} &middot; Due: {escape(str(due))} &middot; Assigned to: {escape(assignee)}
        </p>
      </div>
      <p><a href="{escape(link)}" style="display:inline-block;background:#2563eb;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none">Open dashboard</a></p>
    </div>
    """
    text = f"{heading}\n\n{intro}\n\nTask: {task['title']}\nPriority: {task['priority']}\nDue: {due}\nAssigned to: {assignee}\n\n{link}"
    return html, text


def people_involved(task):
    people = {}
    for person in (task["creator"], task.get("assignee")):
        if person:
            people[person["email"]] = person
    return people.values()


def notify_task_created(task, actor):
    assignee = task.get("assignee")
    for person in people_involved(task):
        if assignee and person["id"] == assignee["id"] and person["id"] != task["created_by"]:
            subject = f"New task assigned to you: {task['title']}"
            heading = "A new task was assigned to you"
            intro = f"{actor['name']} assigned you a task."
        else:
            subject = f"Task created: {task['title']}"
            heading = "Your task was created"
            intro = "Your new task is now on the board."
        html, text = render(heading, intro, task)
        send_async(person["email"], subject, html, text)


def notify_task_completed(task, actor):
    for person in people_involved(task):
        subject = f"Task completed: {task['title']}"
        html, text = render(
            "A task was completed", f"{actor['name']} marked this task as completed.", task
        )
        send_async(person["email"], subject, html, text)