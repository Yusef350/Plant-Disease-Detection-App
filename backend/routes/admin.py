"""
Admin routes — /api/admin (requires admin role)
"""

from flask import Blueprint, request, jsonify

from middleware.auth import require_admin
from models import user as user_model
from models import disease as disease_model
from models import scan as scan_model
from models.db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ── GET /api/admin/users — list all users ──────────────────────────────


@admin_bp.route("/users", methods=["GET"])
@require_admin
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    users = user_model.list_all_users(page, per_page)
    total = user_model.count_users()
    return jsonify({
        "users": users,
        "total": total,
        "page": page,
        "perPage": per_page,
    }), 200


# ── POST /api/admin/diseases — create a disease entry ─────────────────


@admin_bp.route("/diseases", methods=["POST"])
@require_admin
def create_disease():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        return jsonify({"error": "Disease name is required"}), 400

    # Check duplicate
    if disease_model.find_by_name(data["name"]):
        return jsonify({"error": "Disease already exists"}), 409

    disease = disease_model.create_disease(data)
    return jsonify({"disease": disease}), 201


# ── PUT /api/admin/diseases/<id> — update a disease ───────────────────


@admin_bp.route("/diseases/<disease_id>", methods=["PUT"])
@require_admin
def update_disease(disease_id: str):
    data = request.get_json(silent=True) or {}
    disease = disease_model.update_disease(disease_id, data)
    if not disease:
        return jsonify({"error": "Disease not found"}), 404
    return jsonify({"disease": disease}), 200


# ── DELETE /api/admin/diseases/<id> — delete a disease ────────────────


@admin_bp.route("/diseases/<disease_id>", methods=["DELETE"])
@require_admin
def delete_disease(disease_id: str):
    success = disease_model.delete_disease(disease_id)
    if not success:
        return jsonify({"error": "Disease not found"}), 404
    return jsonify({"message": "Disease deleted"}), 200


# ── GET /api/admin/analytics — system stats ───────────────────────────


@admin_bp.route("/analytics", methods=["GET"])
@require_admin
def analytics():
    db = get_db()

    total_users = user_model.count_users()
    total_scans = scan_model.count_all()
    total_diseases = disease_model.count()

    # Top 5 most detected diseases
    pipeline = [
        {"$match": {"isHealthy": False}},
        {"$group": {"_id": "$diseaseId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    top_diseases_raw = list(db.diagnoses.aggregate(pipeline))

    top_diseases = []
    for item in top_diseases_raw:
        if item["_id"]:
            d = disease_model.find_by_id(str(item["_id"]))
            if d:
                top_diseases.append({
                    "disease": disease_model.serialize(d),
                    "count": item["count"],
                })

    # Recent scans (last 10)
    recent_scans_raw = list(
        db.scans.find().sort("createdAt", -1).limit(10)
    )
    recent_scans = []
    for s in recent_scans_raw:
        s["id"] = str(s.pop("_id"))
        s["userId"] = str(s["userId"]) if "userId" in s else None
        if "plantId" in s and s["plantId"]:
            s["plantId"] = str(s["plantId"])
        recent_scans.append(s)

    return jsonify({
        "totalUsers": total_users,
        "totalScans": total_scans,
        "totalDiseases": total_diseases,
        "topDiseases": top_diseases,
        "recentScans": recent_scans,
    }), 200
