"""
Flask app — CV Tailor
Routes:
  GET  /          → paste job description UI
  POST /generate  → AI tailoring, stores CV, returns .docx download
  GET  /download  → serve latest CV as .docx
  POST /refine    → refine stored CV via chat, returns JSON {reply, ready}
"""

import io
from flask import Flask, request, render_template, send_file, jsonify
from ai_matcher import tailor_cv, refine_cv
from cv_template import render_cv

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB max request

# Single-user in-memory state
_state = {
    "cv_data": None,      # latest tailored CV dict
    "docx_bytes": None,   # latest rendered .docx bytes
}


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

    user_notes = request.form.get("user_notes", "").strip()

    try:
        tailored_data = tailor_cv(job_description, user_notes)
        docx_bytes = render_cv(tailored_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    _state["cv_data"] = tailored_data
    _state["docx_bytes"] = docx_bytes

    selected = tailored_data.get("_selected_resume", "")
    return jsonify({"ready": True, "selected_resume": selected})


@app.route("/download")
def download():
    if not _state["docx_bytes"]:
        return jsonify({"error": "No CV generated yet."}), 404

    return send_file(
        io.BytesIO(_state["docx_bytes"]),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name="Melda_Akan_CV.docx",
    )


@app.route("/refine", methods=["POST"])
def refine():
    if not _state["cv_data"]:
        return jsonify({"error": "Generate a CV first before refining."}), 400

    data = request.get_json()
    user_message = (data or {}).get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        updated_cv, reply = refine_cv(_state["cv_data"], user_message)
        docx_bytes = render_cv(updated_cv)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    _state["cv_data"] = updated_cv
    _state["docx_bytes"] = docx_bytes

    return jsonify({"reply": reply, "ready": True})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
