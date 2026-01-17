import os
import logging
from flask import Flask, render_template, request, jsonify
from engine.ml_engine import password_assistant_with_reuse, initialize_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates_", static_folder="static")

# initialize/load models once
logger.info("Starting Flask Password Assistant application...")
try:
    initialize_models()
    logger.info("Models initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize models: {e}", exc_info=True)
    # Continue anyway - the app can still run with rule-based scoring


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        password = request.form.get("password", "")
        logger.info(f"Processing password analysis request for password of length {len(password)}")
        try:
            result = password_assistant_with_reuse(password)
        except Exception as e:
            logger.error(f"Error analyzing password: {e}", exc_info=True)
            result = {"error": "Failed to analyze password"}
    return render_template("index.html", result=result)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json() or {}
    password = data.get("password", "")
    logger.info(f"API analyze request for password of length {len(password)}")
    try:
        res = password_assistant_with_reuse(password)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in API analyze: {e}", exc_info=True)
        return jsonify({"error": "Failed to analyze password"}), 500


@app.route("/result", methods=["POST"])
def result_page():
    # Accepts form POSTs (from the main page) and renders a standalone result page
    password = request.form.get("password", "")
    res = password_assistant_with_reuse(password)
    return render_template("result.html", result=res)


@app.route("/health")
def health():
    logger.debug("Health check requested")
    return jsonify({"status": "healthy", "service": "password-assistant"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

