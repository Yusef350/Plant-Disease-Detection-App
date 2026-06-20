"""
AI inference service — loads the TensorFlow Keras model once (lazy singleton)
and exposes a `predict(image_bytes)` function.
"""

import io
import numpy as np
from PIL import Image

from config import Config

# ── Class labels (38 classes) ────────────────────────────────────────────
CLASS_NAMES: list[str] = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Lazy-loaded model reference
_model = None


def _load_model():
    """Load the Keras model once and cache it."""
    global _model
    if _model is None:
        import tensorflow as tf

        _model = tf.keras.models.load_model(Config.MODEL_PATH)
    return _model


def predict(image_bytes: bytes) -> dict:
    """
    Run inference on raw image bytes.

    Returns:
        {
            "className": "Tomato___Late_blight",
            "plantName": "Tomato",
            "diseaseName": "Late blight",
            "confidence": 0.9723,
            "isHealthy": False,
        }
    """
    model = _load_model()

    # Pre-process: resize to 128×128, normalise to [0, 1]
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((128, 128))
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)  # batch dimension

    predictions = model.predict(arr, verbose=0)
    idx = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][idx])
    class_name = CLASS_NAMES[idx]

    # Parse plant name and disease name from the label
    parts = class_name.split("___")
    plant_name = parts[0].replace("_", " ")
    raw_disease = parts[1] if len(parts) > 1 else ""
    is_healthy = raw_disease.lower() == "healthy"
    disease_name = "Healthy" if is_healthy else raw_disease.replace("_", " ")

    return {
        "className": class_name,
        "plantName": plant_name,
        "diseaseName": disease_name,
        "confidence": round(confidence, 4),
        "isHealthy": is_healthy,
    }
