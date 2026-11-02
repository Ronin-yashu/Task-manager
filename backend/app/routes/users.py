from flask import Blueprint, jsonify
from ..db import supabase
from ..utils import login_required

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("")
@login_required
def list_users():
    result = (
        supabase.table("users")
        .select("id,name,email,avatar_url")
        .order("name")
        .execute()
    )
    return jsonify(result.data)