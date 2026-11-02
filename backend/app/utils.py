from functools import wraps
import jwt
from flask import request, g, jsonify
from .config import Config
from .db import supabase


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify({"error": "Invalid or expired token"}), 401
        result = (
            supabase.table("users")
            .select("*")
            .eq("id", payload["sub"])
            .limit(1)
            .execute()
        )
        if not result.data:
            return jsonify({"error": "User not found"}), 401
        g.user = result.data[0]
        return fn(*args, **kwargs)

    return wrapper