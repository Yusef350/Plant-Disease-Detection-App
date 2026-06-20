"""
Tests the same image TWICE — once with raw values, once normalized.
The one with higher MAX confidence is using the correct normalization.
"""
import tensorflow as tf
import numpy as np
import os

CLASS_NAMES = ['Apple___Apple_scab','Apple___Black_rot','Apple___Cedar_apple_rust','Apple___healthy',
    'Blueberry___healthy','Cherry_(including_sour)___Powdery_mildew','Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot','Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight','Corn_(maize)___healthy','Grape___Black_rot',
    'Grape___Esca_(Black_Measles)','Grape___Leaf_blight_(Isariopsis_Leaf_Spot)','Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)','Peach___Bacterial_spot','Peach___healthy',
    'Pepper,_bell___Bacterial_spot','Pepper,_bell___healthy','Potato___Early_blight',
    'Potato___Late_blight','Potato___healthy','Raspberry___healthy','Soybean___healthy',
    'Squash___Powdery_mildew','Strawberry___Leaf_scorch','Strawberry___healthy',
    'Tomato___Bacterial_spot','Tomato___Early_blight','Tomato___Late_blight','Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot','Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot','Tomato___Tomato_Yellow_Leaf_Curl_Virus','Tomato___Tomato_mosaic_virus',
    'Tomato___healthy']

model = tf.keras.models.load_model('trained_plant_disease_model.keras')

# Use the latest uploaded image
uploads = sorted([f for f in os.listdir('uploads') if f.endswith('.jpg')])
img_path = os.path.join('uploads', uploads[-1])
print(f"Testing: {uploads[-1]}\n")

img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128))
arr = tf.keras.preprocessing.image.img_to_array(img)

# --- Test 1: RAW 0-255 (no normalization) ---
preds_raw = model.predict(np.array([arr]), verbose=0)[0]
idx_raw = int(np.argmax(preds_raw))
print(f"[RAW 0-255]  -> {CLASS_NAMES[idx_raw]}  confidence: {preds_raw[idx_raw]*100:.2f}%")

# --- Test 2: NORMALIZED 0-1 (/255) ---
preds_norm = model.predict(np.array([arr / 255.0]), verbose=0)[0]
idx_norm = int(np.argmax(preds_norm))
print(f"[NORM /255]  -> {CLASS_NAMES[idx_norm]}  confidence: {preds_norm[idx_norm]*100:.2f}%")

print()
if preds_raw[idx_raw] > preds_norm[idx_norm]:
    print("*** VERDICT: Model expects RAW 0-255 (no normalization) ***")
else:
    print("*** VERDICT: Model expects NORMALIZED /255 ***")
