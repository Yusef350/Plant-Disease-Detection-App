"""
User / Profile routes — /api/users
"""

from datetime import datetime
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
    unique_plants = diagnosis_model.get_unique_plants_count(g.user_id)

    return (
        jsonify(
            {
                "user": user,
                "stats": {
                    "totalScans": total_scans,
                    "plantsScanned": unique_plants,
                    "mostDetected": most_detected.get("disease") if most_detected else None,
                },
            }
        ),
        200,
    )


@users_bp.route("/dashboard", methods=["GET"])
@require_auth
def get_dashboard():
    """Returns data for the home screen."""
    user_id = g.user_id
    from models.user import find_by_id, serialize
    from models.scan import list_by_user
    from models.diagnosis import list_by_user_scans
    from models.disease import find_by_id as find_disease, serialize as d_serialize

    user = find_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 1. Greeting
    hour = datetime.now().hour
    greeting_map = {
        (0, 12): "Good morning",
        (12, 17): "Good afternoon",
        (17, 24): "Good evening",
    }
    greeting = next(msg for (start, end), msg in greeting_map.items() if start <= hour < end)

    # 2. Recent Diagnoses (Limit 5)
    scans = list_by_user(user_id, limit=5)
    diagnoses = list_by_user_scans([s["id"] for s in scans])

    recent_diagnoses = []
    for s in scans:
        diag = next((d for d in diagnoses if d["scanId"] == s["id"]), None)
        disease = find_disease(str(diag["diseaseId"])) if diag and diag.get("diseaseId") else None

        recent_diagnoses.append({
            "id": s["id"],
            "plantName": s["plantName"],
            "diseaseName": s["diseaseName"],
            "confidence": f"{int(diag['confidence'] * 100)}%" if diag else None,
            "imageUrl": s["imageUrl"],
            "createdAt": s["createdAt"],
            "diseaseInfo": d_serialize(disease) if disease else None
        })

    return jsonify({
        "greeting": f"Hello, {user.get('name', 'User')} 👋",
        "subtitle": "How are your plants today?",
        "recentDiagnoses": recent_diagnoses,
        "dailyTip": {
            "title": "Daily Tip",
            "content": "Water your plants early in the morning for better absorption.",
            "icon": "lightbulb"
        }
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
