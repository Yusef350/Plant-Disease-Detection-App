"""
AI inference service — mirrors exactly the prediction logic in
machineLearning/Plant_Disease_Prediction/main.py
"""

import io
import numpy as np
import tensorflow as tf

from config import Config

# ── Class labels — copied directly from main.py, same order, no sorting ──────
CLASS_NAMES: list[str] = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

# Lazy-loaded model reference
_model = None


def _load_model():
    """Load the Keras model once and cache it (lazy singleton)."""
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(Config.MODEL_PATH)
    return _model


def predict(image_bytes: bytes) -> dict:
    """
    Run inference on raw image bytes.

    Mirrors main.py logic exactly:
        image  = load_img(path, target_size=(128,128))
        arr    = img_to_array(image)          # float32, 0-255, NO /255
        batch  = np.array([arr])
        preds  = model.predict(batch)
        index  = np.argmax(preds)

    Returns:
        {
            "className":   "Tomato___Late_blight",
            "plantName":   "Tomato",
            "diseaseName": "Late blight",
            "confidence":  0.9723,
            "isHealthy":   False,
        }
    """
    model = _load_model()

    # ── Preprocessing (identical to main.py) ─────────────────────────────────
    # tf.keras.preprocessing.image.load_img  → PIL image resized to 128x128
    # tf.keras.preprocessing.image.img_to_array → float32 ndarray, values 0-255
    # np.array([arr])                          → shape (1, 128, 128, 3)
    # model.predict(batch)                     → NO /255 normalization applied
    img = tf.keras.preprocessing.image.load_img(
        io.BytesIO(image_bytes), target_size=(128, 128)
    )
    arr = tf.keras.preprocessing.image.img_to_array(img)   # raw 0-255, no normalization
    batch = np.array([arr])                                  # (1, 128, 128, 3)

    predictions = model.predict(batch, verbose=0)
    idx = int(np.argmax(predictions))                        # same as main.py
    confidence = float(predictions[0][idx])
    class_name = CLASS_NAMES[idx]

    # ── Parse plant / disease names ───────────────────────────────────────────
    parts = class_name.split("___")
    plant_name = parts[0].replace("_", " ")
    raw_disease = parts[1] if len(parts) > 1 else ""
    is_healthy = raw_disease.lower() == "healthy"
    disease_name = "Healthy" if is_healthy else raw_disease.replace("_", " ")

    return {
        "className":   class_name,
        "plantName":   plant_name,
        "diseaseName": disease_name,
        "confidence":  round(confidence, 4),
        "isHealthy":   is_healthy,
    }
