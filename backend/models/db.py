"""
MongoDB client singleton and database accessor.
"""

from pymongo import MongoClient
from pymongo.database import Database

from config import Config

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return a cached MongoClient instance."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_db() -> Database:
    """Return the application database."""
    return get_client()[Config.MONGO_DB_NAME]


def init_db() -> None:
    """Create indexes on first startup."""
    db = get_db()

    # Users — unique email
    db.users.create_index("email", unique=True)

    # Scans — fast lookup by user + sort by date
    db.scans.create_index([("userId", 1), ("createdAt", -1)])

    # Diagnoses — lookup by scan
    db.diagnoses.create_index("scanId")

    # Diseases — unique name for lookups
    db.diseases.create_index("name", unique=True)

    # Plants — unique common name
    db.plants.create_index("commonName", unique=True)
