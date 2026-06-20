"""
User / Profile routes — /api/users
"""

from flask import Blueprint, request, jsonify, g

from middleware.auth import require_auth
from models import user as user_model
from models import scan as scan_model
from models import diagnosis as diagnosis_model

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# ── GET /api/users/profile — current user profile + stats ─────────────


@users_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    doc = user_model.find_by_id(g.user_id)
    if not doc:
        return jsonify({"error": "User not found"}), 404

    user = user_model.serialize(doc)

    # Statistics
    total_scans = scan_model.count_by_user(g.user_id)
    most_detected = diagnosis_model.get_most_detected_disease(g.user_id)

    return jsonify({
        "user": user,
        "stats": {
            "totalScans": total_scans,
            "mostDetectedDisease": most_detected,
        },
    }), 200


# ── PUT /api/users/profile — update display name / email ──────────────


@users_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    data = request.get_json(silent=True) or {}
    doc = user_model.update_profile(g.user_id, data)
    if not doc:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_model.serialize(doc)}), 200


# ── PUT /api/users/password — change password ─────────────────────────


@users_bp.route("/password", methods=["PUT"])
@require_auth
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get("currentPassword", "")
    new_password = data.get("newPassword", "")

    if not current_password or not new_password:
        return jsonify({"error": "currentPassword and newPassword are required"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    # Verify current password
    doc = user_model.find_by_id(g.user_id)
    if not doc:
        return jsonify({"error": "User not found"}), 404
    if not user_model.check_password(current_password, doc["passwordHash"]):
        return jsonify({"error": "Current password is incorrect"}), 401

    user_model.update_password(g.user_id, new_password)
    return jsonify({"message": "Password updated successfully"}), 200
