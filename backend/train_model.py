"""
Train the plant disease detection model from scratch.

Dataset: PlantVillage (38 classes, ~87K images)
Download from: https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset

Usage:
    1. Download and unzip the dataset so that you have:
       - train/         (contains 38 class subdirectories)
       - valid/         (contains 38 class subdirectories)
    2. Place this script alongside those folders OR set DATASET_DIR below.
    3. Run: python train_model.py

The trained model will be saved as 'trained_plant_disease_model.keras'
in the backend/ folder (MODEL_OUTPUT_PATH).
"""

import os
import json
import tensorflow as tf

# ── Configuration ─────────────────────────────────────────────────────────────

# Path to the folder containing 'train' and 'valid' subdirectories
# Change this if your dataset is elsewhere
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VALID_DIR = os.path.join(DATASET_DIR, "valid")

# Output path — saves directly into backend/ so ai_service.py can load it
MODEL_OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "trained_plant_disease_model.keras"
)

IMAGE_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.0001
NUM_CLASSES = 38

# ── Load datasets ─────────────────────────────────────────────────────────────

print("Loading training dataset...")
training_set = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels="inferred",
    label_mode="categorical",
    color_mode="rgb",
    batch_size=BATCH_SIZE,
    image_size=IMAGE_SIZE,
    shuffle=True,
    interpolation="bilinear",
)

print("Loading validation dataset...")
validation_set = tf.keras.utils.image_dataset_from_directory(
    VALID_DIR,
    labels="inferred",
    label_mode="categorical",
    color_mode="rgb",
    batch_size=BATCH_SIZE,
    image_size=IMAGE_SIZE,
    shuffle=True,
    interpolation="bilinear",
)

# ── Normalise pixel values ────────────────────────────────────────────────────

normalisation_layer = tf.keras.layers.Rescaling(1.0 / 255)
training_set = training_set.map(lambda x, y: (normalisation_layer(x), y))
validation_set = validation_set.map(lambda x, y: (normalisation_layer(x), y))

# ── Build model (exact architecture from Train_plant_disease.ipynb) ───────────

print("Building model...")
cnn = tf.keras.models.Sequential()

# Block 1 — 32 filters
cnn.add(tf.keras.layers.Conv2D(filters=32, kernel_size=3, padding="same", activation="relu", input_shape=[128, 128, 3]))
cnn.add(tf.keras.layers.Conv2D(filters=32, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

# Block 2 — 64 filters
cnn.add(tf.keras.layers.Conv2D(filters=64, kernel_size=3, padding="same", activation="relu"))
cnn.add(tf.keras.layers.Conv2D(filters=64, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

# Block 3 — 128 filters
cnn.add(tf.keras.layers.Conv2D(filters=128, kernel_size=3, padding="same", activation="relu"))
cnn.add(tf.keras.layers.Conv2D(filters=128, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

# Block 4 — 256 filters
cnn.add(tf.keras.layers.Conv2D(filters=256, kernel_size=3, padding="same", activation="relu"))
cnn.add(tf.keras.layers.Conv2D(filters=256, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

# Block 5 — 512 filters
cnn.add(tf.keras.layers.Conv2D(filters=512, kernel_size=3, padding="same", activation="relu"))
cnn.add(tf.keras.layers.Conv2D(filters=512, kernel_size=3, activation="relu"))
cnn.add(tf.keras.layers.MaxPool2D(pool_size=2, strides=2))

cnn.add(tf.keras.layers.Dropout(0.25))
cnn.add(tf.keras.layers.Flatten())
cnn.add(tf.keras.layers.Dense(units=1500, activation="relu"))
cnn.add(tf.keras.layers.Dropout(0.4))

# Output
cnn.add(tf.keras.layers.Dense(units=NUM_CLASSES, activation="softmax"))

# ── Compile ───────────────────────────────────────────────────────────────────

cnn.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

cnn.summary()

# ── Train ─────────────────────────────────────────────────────────────────────

print(f"\nTraining for {EPOCHS} epochs...")
training_history = cnn.fit(
    x=training_set,
    validation_data=validation_set,
    epochs=EPOCHS,
)

# ── Save model ────────────────────────────────────────────────────────────────

print(f"\nSaving model to: {MODEL_OUTPUT_PATH}")
cnn.save(MODEL_OUTPUT_PATH)
print("✅ Model saved successfully!")

# ── Save training history ─────────────────────────────────────────────────────

history_path = os.path.join(os.path.dirname(MODEL_OUTPUT_PATH), "training_hist.json")
with open(history_path, "w") as f:
    json.dump(training_history.history, f)
print(f"✅ Training history saved to: {history_path}")

# ── Print final metrics ───────────────────────────────────────────────────────

final_train_acc = training_history.history["accuracy"][-1]
final_val_acc = training_history.history["val_accuracy"][-1]
print(f"\nFinal Training Accuracy:   {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
print(f"Final Validation Accuracy: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
