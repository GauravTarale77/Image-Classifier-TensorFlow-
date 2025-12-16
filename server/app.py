from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

model = tf.keras.models.load_model("animal_classifier_mobilenetv2.keras")

CLASS_NAMES = ["cat", "cow", "dog", "elephant", "horse"]

def preprocess(image):
    image = image.resize((224, 224))
    image = np.array(image)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    return image

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    img = Image.open(request.files["file"]).convert("RGB")
    img = preprocess(img)

    preds = model.predict(img)[0]
    idx = np.argmax(preds)

    return jsonify({
        "prediction": CLASS_NAMES[idx],
    })

@app.route("/")
def home():
    return "Animal Image Classifier API Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
