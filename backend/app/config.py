import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ["JWT_SECRET"]
    JWT_SECRET = os.environ["JWT_SECRET"]
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")
    COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE = os.environ.get("COOKIE_SAMESITE", "Lax")