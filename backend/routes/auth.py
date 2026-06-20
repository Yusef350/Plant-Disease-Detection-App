"""
Auth routes — /api/auth
"""

import re

from flask import Blueprint, request, jsonify

from models import user as user_model
from middleware.auth import create_token, require_auth
from flask import g

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Simple email regex
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _validate_register(data: dict) -> str | None:
    """Return error message or None."""
    if not data.get("displayName") or len(data["displayName"].strip()) < 2:
        return "Display name must be at least 2 characters"
    if not data.get("email") or not _EMAIL_RE.match(data["email"]):
        return "Valid email is required"
    if not data.get("password") or len(data["password"]) < 6:
        return "Password must be at least 6 characters"
    return None


# ── POST /api/auth/register ────────────────────────────────────────────


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    err = _validate_register(data)
    if err:
        return jsonify({"error": err}), 400

    # Check duplicate
    if user_model.find_by_email(data["email"]):
        return jsonify({"error": "Email already registered"}), 409

    user = user_model.create_user(
        display_name=data["displayName"],
        email=data["email"],
        password=data["password"],
    )
    token = create_token(user["id"], user.get("role", "user"))
    return jsonify({"user": user, "token": token}), 201


# ── POST /api/auth/login ───────────────────────────────────────────────


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    doc = user_model.find_by_email(email)
    if not doc or not user_model.check_password(password, doc["passwordHash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    user_model.touch_login(str(doc["_id"]))
    user = user_model.serialize(doc)
    token = create_token(user["id"], user.get("role", "user"))
    return jsonify({"user": user, "token": token}), 200


# ── GET /api/auth/me ───────────────────────────────────────────────────


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    doc = user_model.find_by_id(g.user_id)
    if not doc:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_model.serialize(doc)}), 200
