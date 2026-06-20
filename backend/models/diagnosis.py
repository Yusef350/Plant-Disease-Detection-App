"""
Diagnosis model helpers — CRUD for the `diagnoses` collection.
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo.collection import Collection

from models.db import get_db


def _col() -> Collection:
    return get_db().diagnoses


def serialize(doc: dict) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    if "scanId" in doc and isinstance(doc["scanId"], ObjectId):
        doc["scanId"] = str(doc["scanId"])
    if "diseaseId" in doc and isinstance(doc["diseaseId"], ObjectId):
        doc["diseaseId"] = str(doc["diseaseId"])
    return doc


def create_diagnosis(
    scan_id: str,
    disease_id: str | None,
    confidence: float,
    is_healthy: bool,
) -> dict:
    doc = {
        "scanId": ObjectId(scan_id),
        "diseaseId": ObjectId(disease_id) if disease_id else None,
        "confidence": round(confidence, 4),
        "isHealthy": is_healthy,
        "createdAt": datetime.now(timezone.utc),
    }
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def find_by_scan(scan_id: str) -> dict | None:
    try:
        return _col().find_one({"scanId": ObjectId(scan_id)})
    except Exception:
        return None


def list_by_user_scans(scan_ids: list[str]) -> list[dict]:
    """Return diagnoses for a list of scan ObjectId strings."""
    oids = [ObjectId(s) for s in scan_ids]
    cursor = _col().find({"scanId": {"$in": oids}})
    return [serialize(doc) for doc in cursor]


def get_most_detected_disease(user_id: str) -> dict | None:
    """Aggregate top disease for a user across their scans."""
    db = get_db()
    pipeline = [
        {"$match": {"userId": ObjectId(user_id)}},
        {
            "$lookup": {
                "from": "diagnoses",
                "localField": "_id",
                "foreignField": "scanId",
                "as": "diagnosis",
            }
        },
        {"$unwind": "$diagnosis"},
        {"$match": {"diagnosis.isHealthy": False}},
        {"$group": {"_id": "$diagnosis.diseaseId", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]
    results = list(db.scans.aggregate(pipeline))
    if not results:
        return None

    from models.disease import find_by_id, serialize as d_serialize

    disease = find_by_id(str(results[0]["_id"]))
    if disease:
        return {"disease": d_serialize(disease), "count": results[0]["count"]}
    return None
