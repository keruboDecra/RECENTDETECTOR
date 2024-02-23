from flask import Flask, request, jsonify, render_template
import re
import nltk
from PIL import Image
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import joblib
import os
model_pipeline = joblib.load('sgd_classifier_model.joblib')

nltk.download('stopwords')
nltk.download('wordnet')
app = Flask(__name__)

label_encoder = joblib.load('label_encoder.joblib')

# Load the logo image
logo = Image.open('logo.png')

# Function to clean and preprocess text
def preprocess_text(text):
    text = re.sub(r'http\S+|www\S+|@\S+|#\S+|[^A-Za-z\s]', '', text)
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

# Function for binary cyberbullying detection
def binary_cyberbullying_detection(text):
    try:
        # Preprocess the input text
        preprocessed_text = preprocess_text(text)

        # Make prediction using the loaded pipeline
        prediction = model_pipeline.predict([preprocessed_text])

        # Check for offensive words
        with open('en.txt', 'r') as f:
            offensive_words = [line.strip() for line in f]

        offending_words = [word for word in preprocessed_text.split() if word in offensive_words]

        return bool(prediction[0]), offending_words
    except Exception as e:
        return None, None

# Function for multi-class cyberbullying detection
def multi_class_cyberbullying_detection(text):
    try:
        # Preprocess the input text
        preprocessed_text = preprocess_text(text)

        # Make prediction
        decision_function_values = model_pipeline.decision_function([preprocessed_text])[0]

        # Get the predicted class index
        predicted_class_index = np.argmax(decision_function_values)

        # Get the predicted class label using the label encoder
        predicted_class_label = label_encoder.inverse_transform([predicted_class_index])[0]

        return predicted_class_label
    except Exception as e:
        return None

def format_offensive_words(offensive_words):
    return ', '.join(offensive_words)

@app.route('/')
def welcome():
    return """<div>
    <h1>Welcome to the Cyberbullying Detection API!</h1>
    <p>This API allows you to detect cyberbullying in text. Send a POST request to /detect with the 'user_input' parameter to analyze text.</p>
    <p>Check the documentation for more details on how to use the API.</p>
    </div>"""

@app.route('/detect', methods=['POST'])
def detect():
    user_input = request.form['user_input']

    # Make binary prediction and check for offensive words
    binary_result, offensive_words = binary_cyberbullying_detection(user_input)

    # Make multi-class prediction
    multi_class_result = multi_class_cyberbullying_detection(user_input)

    result = {
        "message": "Your text is safe to send.",
        "details": {
            "offensive": bool(binary_result),
            "offensive_reasons": offensive_words if bool(binary_result) else None,
            "multi_class_result": multi_class_result if multi_class_result else None,
        }
    }

    if bool(binary_result):
        result["message"] = "This text is unsafe."

        if offensive_words:
            result["details"]["message"] = f"Detected offensive words: {format_offensive_words(offensive_words)}"

    elif multi_class_result:
        result["message"] = f"Please edit your text before resending. Your text may be interpreted as {multi_class_result.replace('_', ' ').title()} by other users."

    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("PORT", default=5000), debug=False)