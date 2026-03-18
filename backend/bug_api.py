from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load the trained pipeline (includes TF-IDF + classifier)
model = joblib.load("bug_severity_model.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"error": "Empty text provided"}), 400
    
    prediction = model.predict([text])[0]
    return jsonify({"severity": prediction})

if __name__ == "__main__":
    print("🚀 Running Flask API on http://127.0.0.1:5000/")
    app.run(debug=True)
