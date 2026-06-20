"""
Plant model helpers — CRUD for the `plants` collection.
"""

from bson import ObjectId
from pymongo.collection import Collection

from models.db import get_db


def _col() -> Collection:
    return get_db().plants


def serialize(doc: dict) -> dict:
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc


def create_plant(data: dict) -> dict:
    doc = {
        "commonName": data["commonName"],
        "scientificName": data.get("scientificName", ""),
        "imageUrl": data.get("imageUrl", ""),
    }
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def find_by_id(plant_id: str) -> dict | None:
    try:
        return _col().find_one({"_id": ObjectId(plant_id)})
    except Exception:
        return None


def find_by_name(name: str) -> dict | None:
    return _col().find_one({"commonName": name})


def list_all() -> list[dict]:
    return [serialize(doc) for doc in _col().find().sort("commonName", 1)]
