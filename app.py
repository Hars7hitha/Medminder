import os

from flask import Flask, render_template, request, jsonify
from gemini_brain import parse_intent
from orchestrator import handle_intent

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    try:
        parsed = parse_intent(user_input)
        intent = parsed.get("intent")
        params = parsed.get("params", {})
        result = handle_intent(intent, params)
        return jsonify({"response": result, "intent": intent})
    except Exception as e:
        return jsonify({"response": f"Error: {e}", "intent": "error"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)