"""
Disease routes — /api/diseases (public, read-only)
"""

from flask import Blueprint, request, jsonify

from models import disease as disease_model

diseases_bp = Blueprint("diseases", __name__, url_prefix="/api/diseases")


# ── GET /api/diseases — list all diseases ──────────────────────────────


@diseases_bp.route("", methods=["GET"])
def list_diseases():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    diseases = disease_model.list_all(page, per_page)
    total = disease_model.count()
    return jsonify({
        "diseases": diseases,
        "total": total,
        "page": page,
        "perPage": per_page,
    }), 200


# ── GET /api/diseases/<id> — disease detail ───────────────────────────


@diseases_bp.route("/<disease_id>", methods=["GET"])
def get_disease(disease_id: str):
    doc = disease_model.find_by_id(disease_id)
    if not doc:
        return jsonify({"error": "Disease not found"}), 404
    return jsonify({"disease": disease_model.serialize(doc)}), 200
