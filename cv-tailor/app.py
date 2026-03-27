"""
Flask app — CV Tailor
Routes:
  GET  /          → paste job description UI
  POST /generate  → runs AI matcher + PDF render, returns PDF download
"""

import io
from flask import Flask, request, render_template, send_file, jsonify
from ai_matcher import tailor_cv
from cv_template import render_cv

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB max request


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    job_description = request.form.get("job_description", "").strip()

    if not job_description:
        return jsonify({"error": "Job description cannot be empty."}), 400

    if len(job_description) < 50:
        return jsonify({"error": "Job description seems too short. Please paste the full text."}), 400

    try:
        tailored_data = tailor_cv(job_description)
        pdf_bytes = render_cv(tailored_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Melda_Akan_CV.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
