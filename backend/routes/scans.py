"""
Scan routes — /api/scans
Handles image upload → AI inference → save scan + diagnosis.
"""

from flask import Blueprint, request, jsonify, g

from middleware.auth import require_auth
from models import scan as scan_model
from models import diagnosis as diagnosis_model
from models import disease as disease_model
from models import plant as plant_model
from services import ai_service, storage_service

scans_bp = Blueprint("scans", __name__, url_prefix="/api/scans")


# ── POST /api/scans — upload image & run inference ─────────────────────


@scans_bp.route("", methods=["POST"])
@require_auth
def create_scan():
    if "image" not in request.files:
        return jsonify({"error": "Image file is required (field name: 'image')"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    image_bytes = file.read()
    if len(image_bytes) == 0:
        return jsonify({"error": "Empty file"}), 400

    # 1. Upload image to storage
    try:
        image_url = storage_service.upload_image(image_bytes, file.filename)
    except Exception as e:
        return jsonify({"error": f"Image upload failed: {str(e)}"}), 500

    # 2. Run AI inference
    try:
        prediction = ai_service.predict(image_bytes)
    except Exception as e:
        return jsonify({"error": f"AI inference failed: {str(e)}"}), 500

    # 3. Resolve plant reference
    plant_doc = plant_model.find_by_name(prediction["plantName"])
    plant_id = str(plant_doc["_id"]) if plant_doc else None

    # 4. Save scan
    scan = scan_model.create_scan(
        user_id=g.user_id,
        image_url=image_url,
        plant_id=plant_id,
        status="completed",
    )

    # 5. Resolve disease reference
    disease_doc = disease_model.find_by_name(prediction["className"])
    disease_id = str(disease_doc["_id"]) if disease_doc else None

    # 6. Save diagnosis
    diagnosis = diagnosis_model.create_diagnosis(
        scan_id=scan["id"],
        disease_id=disease_id,
        confidence=prediction["confidence"],
        is_healthy=prediction["isHealthy"],
    )

    # 7. Attach disease details    # Join disease details
    disease_data = None
    if disease_doc:
        disease_data = disease_model.serialize(disease_doc)

    return (
        jsonify(
            {
                "scan": scan,
                "diagnosis": diagnosis,
                "prediction": prediction,
                "disease": disease_data,
            }
        ),
        201,
    )


# ── GET /api/scans — list user's scan history ─────────────────────────


@scans_bp.route("", methods=["GET"])
@require_auth
def list_scans():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    scans = scan_model.list_by_user(g.user_id, page, per_page)
    total = scan_model.count_by_user(g.user_id)

    # Attach diagnosis to each scan
    for scan in scans:
        diag = diagnosis_model.find_by_scan(scan["id"])
        scan["diagnosis"] = diag
        if diag and diag.get("diseaseId"):
            disease_doc = disease_model.find_by_id(diag["diseaseId"])
            scan["disease"] = disease_model.serialize(disease_doc) if disease_doc else None
        else:
            scan["disease"] = None

    return jsonify({
        "scans": scans,
        "total": total,
        "page": page,
        "perPage": per_page,
    }), 200


# ── GET /api/scans/<id> — single scan detail ──────────────────────────


@scans_bp.route("/<scan_id>", methods=["GET"])
@require_auth
def get_scan(scan_id: str):
    scan_doc = scan_model.find_by_id(scan_id)
    if not scan_doc:
        return jsonify({"error": "Scan not found"}), 404

    # Verify ownership (unless admin)
    if str(scan_doc["userId"]) != g.user_id and g.user_role != "admin":
        return jsonify({"error": "Access denied"}), 403

    scan = scan_model.serialize(scan_doc)

    # Attach diagnosis
    diag = diagnosis_model.find_by_scan(scan["id"])
    scan["diagnosis"] = diag

    # Attach disease details
    disease_info = None
    if diag and diag.get("diseaseId"):
        disease_doc = disease_model.find_by_id(diag["diseaseId"])
        disease_info = disease_model.serialize(disease_doc) if disease_doc else None
    scan["disease"] = disease_info

    # Attach plant details
    plant_info = None
    if scan.get("plantId"):
        plant_doc = plant_model.find_by_id(scan["plantId"])
        plant_info = plant_model.serialize(plant_doc) if plant_doc else None
    scan["plant"] = plant_info

    return jsonify({"scan": scan}), 200
