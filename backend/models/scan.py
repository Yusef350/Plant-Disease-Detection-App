"""
Scan model helpers — CRUD for the `scans` collection.
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo.collection import Collection

from models.db import get_db


def _col() -> Collection:
    return get_db().scans


def serialize(doc: dict) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    # Convert ObjectIds to strings
    if "userId" in doc and isinstance(doc["userId"], ObjectId):
        doc["userId"] = str(doc["userId"])
    if "plantId" in doc and isinstance(doc["plantId"], ObjectId):
        doc["plantId"] = str(doc["plantId"])
    return doc


def create_scan(
    user_id: str,
    image_url: str,
    plant_id: str | None = None,
    status: str = "completed",
) -> dict:
    doc = {
        "userId": ObjectId(user_id),
        "imageUrl": image_url,
        "status": status,
        "plantId": ObjectId(plant_id) if plant_id else None,
        "createdAt": datetime.now(timezone.utc),
    }
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def find_by_id(scan_id: str) -> dict | None:
    try:
        return _col().find_one({"_id": ObjectId(scan_id)})
    except Exception:
        return None


def list_by_user(user_id: str, page: int = 1, per_page: int = 20) -> list[dict]:
    skip = (page - 1) * per_page
    cursor = (
        _col()
        .find({"userId": ObjectId(user_id)})
        .sort("createdAt", -1)
        .skip(skip)
        .limit(per_page)
    )
    return [serialize(doc) for doc in cursor]


def count_by_user(user_id: str) -> int:
    return _col().count_documents({"userId": ObjectId(user_id)})


def count_all() -> int:
    return _col().count_documents({})
