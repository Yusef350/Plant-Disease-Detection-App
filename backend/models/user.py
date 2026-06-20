"""
User model helpers — CRUD operations on the `users` collection.
"""

from datetime import datetime, timezone

import bcrypt
from bson import ObjectId
from pymongo.collection import Collection

from models.db import get_db


def _col() -> Collection:
    return get_db().users


# ── Helpers ──────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def serialize(doc: dict) -> dict:
    """Convert Mongo document to JSON-safe dict."""
    if doc is None:
        return None
    doc["id"] = str(doc.pop("_id"))
    doc.pop("passwordHash", None)  # never expose hash
    return doc


# ── CRUD ─────────────────────────────────────────────────────────────────


def create_user(display_name: str, email: str, password: str) -> dict:
    now = datetime.now(timezone.utc)
    doc = {
        "email": email.lower().strip(),
        "passwordHash": hash_password(password),
        "displayName": display_name.strip(),
        "role": "user",  # "user" | "admin"
        "createdAt": now,
        "lastLoginAt": now,
    }
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize(doc)


def find_by_email(email: str) -> dict | None:
    return _col().find_one({"email": email.lower().strip()})


def find_by_id(user_id: str) -> dict | None:
    try:
        return _col().find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def update_profile(user_id: str, data: dict) -> dict | None:
    allowed = {"displayName", "email"}
    updates = {k: v for k, v in data.items() if k in allowed and v}
    if "email" in updates:
        updates["email"] = updates["email"].lower().strip()
    if not updates:
        return find_by_id(user_id)
    _col().update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return find_by_id(user_id)


def update_password(user_id: str, new_password: str) -> bool:
    result = _col().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"passwordHash": hash_password(new_password)}},
    )
    return result.modified_count == 1


def touch_login(user_id: str) -> None:
    _col().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"lastLoginAt": datetime.now(timezone.utc)}},
    )


def list_all_users(page: int = 1, per_page: int = 20) -> list[dict]:
    skip = (page - 1) * per_page
    cursor = (
        _col()
        .find({}, {"passwordHash": 0})
        .sort("createdAt", -1)
        .skip(skip)
        .limit(per_page)
    )
    users = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        users.append(doc)
    return users


def count_users() -> int:
    return _col().count_documents({})
