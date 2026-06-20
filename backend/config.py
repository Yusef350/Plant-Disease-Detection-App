"""
Application configuration loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # ── MongoDB ──────────────────────────────────────────────────────────
    MONGO_URI: str = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017",
    )
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "plant_disease_db")

    # ── JWT ──────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "72"))

    # ── Cloudinary (optional) ────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # ── AI Model ─────────────────────────────────────────────────────────
    MODEL_PATH: str = os.getenv("MODEL_PATH", "trained_plant_disease_model.keras")

    # ── Upload fallback (when Cloudinary is not configured) ──────────────
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads"
    )

    @classmethod
    def cloudinary_configured(cls) -> bool:
        return bool(
            cls.CLOUDINARY_CLOUD_NAME
            and cls.CLOUDINARY_API_KEY
            and cls.CLOUDINARY_API_SECRET
        )
