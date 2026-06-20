"""
Image storage service — uploads to Cloudinary when configured,
otherwise saves locally to backend/uploads/.
"""

import os
import uuid
from datetime import datetime

from config import Config


def _ensure_upload_dir() -> str:
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    return Config.UPLOAD_FOLDER


def upload_image(image_bytes: bytes, filename: str = "") -> str:
    """
    Upload image bytes and return a public URL.

    If Cloudinary is configured → upload there and return secure_url.
    Otherwise → save locally and return a relative path.
    """
    if Config.cloudinary_configured():
        return _upload_cloudinary(image_bytes, filename)
    return _save_local(image_bytes, filename)


def _upload_cloudinary(image_bytes: bytes, filename: str) -> str:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True,
    )

    public_id = f"plant_scans/{uuid.uuid4().hex}"
    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=public_id,
        folder="plant_disease",
        resource_type="image",
    )
    return result["secure_url"]


def _save_local(image_bytes: bytes, filename: str) -> str:
    upload_dir = _ensure_upload_dir()
    ext = os.path.splitext(filename)[1] if filename else ".jpg"
    if not ext:
        ext = ".jpg"
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(upload_dir, unique_name)
    with open(path, "wb") as f:
        f.write(image_bytes)
    # Return a URL-style path the frontend can use
    return f"/uploads/{unique_name}"
