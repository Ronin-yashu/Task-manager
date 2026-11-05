import datetime
import jwt
from flask import Blueprint, redirect, make_response, g, jsonify
from ..config import Config
from ..db import supabase
from ..extensions import oauth
from ..utils import login_required

bp = Blueprint("auth", __name__, url_prefix="/auth")

COOKIE_MAX_AGE = 7 * 24 * 60 * 60


@bp.get("/google/login")
def google_login():
    redirect_uri = f"{Config.FRONTEND_URL}/api/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri)


@bp.get("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    info = token["userinfo"]

    row = {
        "google_id": info["sub"],
        "email": info["email"],
        "name": info.get("name"),
        "avatar_url": info.get("picture"),
    }
    result = supabase.table("users").upsert(row, on_conflict="google_id").execute()
    user = result.data[0]

    payload = {
        "sub": user["id"],
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=COOKIE_MAX_AGE),
    }
    access_token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    response = make_response(redirect(f"{Config.FRONTEND_URL}/dashboard"))
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=Config.COOKIE_SECURE,
        samesite=Config.COOKIE_SAMESITE,
        max_age=COOKIE_MAX_AGE,
    )
    return response


@bp.get("/me")
@login_required
def me():
    return jsonify(g.user)


@bp.post("/logout")
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.delete_cookie(
        "access_token",
        secure=Config.COOKIE_SECURE,
        samesite=Config.COOKIE_SAMESITE,
    )
    return response