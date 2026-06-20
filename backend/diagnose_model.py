# Diagnostic script - verifies the model is working and reveals the correct class order.
# Run:  .\venv\Scripts\python.exe diagnose_model.py <path_to_image>
# e.g.: .\venv\Scripts\python.exe diagnose_model.py C:/Users/yusef/Downloads/tomato.jpg

import sys
import io
import numpy as np
from PIL import Image
import tensorflow as tf

# ── The class order TF uses when it reads a dataset from directories on Linux ──
# This is STRICT ALPHABETICAL ORDER (case-sensitive, uppercase A-Z before a-z)
# This is the CORRECT order matching the Kaggle PlantVillage dataset.
CORRECT_CLASS_NAMES = sorted([
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
])

MODEL_PATH = "trained_plant_disease_model.keras"

print("=" * 60)
print("Correct alphabetical class order (as TF sees it):")
print("=" * 60)
for i, name in enumerate(CORRECT_CLASS_NAMES):
    print(f"  [{i:2d}] {name}")

print()

if len(sys.argv) < 2:
    print("⚠️  No image path provided. Run with:")
    print("   .\\venv\\Scripts\\python.exe diagnose_model.py <image_path>")
    sys.exit(0)

image_path = sys.argv[1]
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded")

print(f"\nProcessing image: {image_path}")
img = Image.open(image_path).convert("RGB")
img = img.resize((128, 128))
arr = np.array(img, dtype=np.float32) / 255.0
arr = np.expand_dims(arr, axis=0)

preds = model.predict(arr, verbose=0)[0]
top5_idx = np.argsort(preds)[::-1][:5]

print("\n" + "=" * 60)
print("TOP 5 PREDICTIONS:")
print("=" * 60)
for rank, idx in enumerate(top5_idx, 1):
    print(f"  #{rank}  [{idx:2d}] {CORRECT_CLASS_NAMES[idx]:<50} {preds[idx]*100:.2f}%")

print()
print(f"✅ Final answer: {CORRECT_CLASS_NAMES[top5_idx[0]]}  ({preds[top5_idx[0]]*100:.2f}% confidence)")
