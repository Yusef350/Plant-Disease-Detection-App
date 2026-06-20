"""
JWT authentication middleware.
"""

import functools
from datetime import datetime, timedelta, timezone

import jwt
from flask import request, jsonify, g

from config import Config


def create_token(user_id: str, role: str = "user") -> str:
    """Create a signed JWT for the given user."""
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT. Returns payload or None."""
    try:
        return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def require_auth(fn):
    """Decorator — rejects request if no valid JWT is present."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authorization token required"}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user_id = payload["sub"]
        g.user_role = payload.get("role", "user")
        return fn(*args, **kwargs)

    return wrapper


def require_admin(fn):
    """Decorator — requires valid JWT with admin role."""

    @functools.wraps(fn)
    @require_auth
    def wrapper(*args, **kwargs):
        if g.user_role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper
