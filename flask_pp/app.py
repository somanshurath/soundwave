from flask import Flask, render_template, request, jsonify
import os
import subprocess
from scripts.speech_to_text import speech_to_text

app = Flask(__name__)


@app.route('/')
def index():
    files = []
    try:
        # result = subprocess.run(
        #     ["curl", "http://10.20.17.77:5000/get_file_list"],
        #     capture_output=True, text=True, check=True
        # )
        # files = result.stdout.strip().split("\n")
        return render_template("index.html", files=files)
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)})
    
@app.route('/transcribe', methods=['POST'])
def transcribe():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({"status": "error", "message": "No filename provided"})
    
    try:
        # step 1: get audio file from 10.20.17.77
        # Step 2: run scripts/speech_to_text.py
        # Step 3: render the result in a new page
        result = subprocess.run(
            ["curl", f"http://10.20.17.77:5000/get_file/{filename}"],
            capture_output=True, text=True, check=True
        )
        with open(f"audio/{filename}", "wb") as f:
            f.write(result.stdout)
        text = speech_from_text(f"audio/{filename}")
        return render_template("transcribe.html", text=text)
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6060)
