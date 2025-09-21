import flask
from flask import render_template, redirect, request, jsonify, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from backend import analyze_resume
import uuid

app = flask.Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'temp')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

analyses = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return "No file part", 400
    resume_file = request.files["resume"]
    if resume_file.filename == "":
        return "No selected file", 400

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    orig_filename = secure_filename(resume_file.filename)
    unique_filename = f"{timestamp}_{orig_filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    resume_file.save(file_path)

    res = analyze_resume(unique_filename.rsplit('.', 1)[0], request.form.get("target_job", None))
    job_id = str(uuid.uuid4())
    analyses[job_id] = res

    return jsonify({'result_url': url_for('result', job_id=job_id)})

@app.route("/result/<job_id>")
def result(job_id):
    result_data = analyses.get(job_id)
    print(result_data)
    if not result_data:
        return "Result not found.", 404
    return render_template("result.html", result=result_data)

if __name__ == "__main__":
    app.run(debug=True)
