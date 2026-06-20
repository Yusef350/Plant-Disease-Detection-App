"""
Disease model helpers — CRUD for the `diseases` collection.
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo.collection import Collection

from models.db import get_db


def _col() -> Collection:
    return get_db().diseases


def serialize(doc: dict) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


# ── CRUD ─────────────────────────────────────────────────────────────────


def create_disease(data: dict) -> dict:
    doc = {
        "name": data["name"],
        "description": data.get("description", ""),
        "symptoms": data.get("symptoms", ""),
        "causes": data.get("causes", ""),
        "treatment": data.get("treatment", ""),
        "prevention": data.get("prevention", ""),
        "severity": data.get("severity", "medium"),
        "imageUrl": data.get("imageUrl", ""),
        "createdAt": datetime.now(timezone.utc),
    }
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def find_by_id(disease_id: str) -> dict | None:
    try:
        return _col().find_one({"_id": ObjectId(disease_id)})
    except Exception:
        return None


def find_by_name(name: str) -> dict | None:
    return _col().find_one({"name": name})


def list_all(page: int = 1, per_page: int = 50) -> list[dict]:
    skip = (page - 1) * per_page
    cursor = _col().find().sort("name", 1).skip(skip).limit(per_page)
    return [serialize(doc) for doc in cursor]


def count() -> int:
    return _col().count_documents({})


def update_disease(disease_id: str, data: dict) -> dict | None:
    allowed = {
        "name", "description", "symptoms", "causes",
        "treatment", "prevention", "severity", "imageUrl",
    }
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return serialize(find_by_id(disease_id))
    _col().update_one({"_id": ObjectId(disease_id)}, {"$set": updates})
    return serialize(find_by_id(disease_id))


def delete_disease(disease_id: str) -> bool:
    result = _col().delete_one({"_id": ObjectId(disease_id)})
    return result.deleted_count == 1
