import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:3000",  
)
CORS(app, resources={r"/*": {"origins": FRONTEND_ORIGIN}})

CLASS_NAMES = ["cat", "cow", "dog", "elephant", "horse"]

_model = None
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "animal_classifier_mobilenetv2.keras", 
)


def get_model():
    """
    Load the Keras model once and reuse it.
    This avoids heavy startup cost on Render.
    """
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def preprocess(image: Image.Image) -> np.ndarray:
    """
    Resize and preprocess the image for MobileNetV2.
    """
    image = image.resize((224, 224))
    image = np.array(image)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    return image


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts a multipart/form-data POST with field 'file'
    and returns the predicted animal class.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        img = Image.open(file.stream).convert("RGB")
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    try:
        img_tensor = preprocess(img)
        model = get_model()
        preds = model.predict(img_tensor)[0]
        idx = int(np.argmax(preds))
        prediction = CLASS_NAMES[idx]
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    return jsonify({"prediction": prediction})


@app.route("/")
def home():
    """
    Lightweight health check route.
    """
    return "Animal Image Classifier API Running"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
