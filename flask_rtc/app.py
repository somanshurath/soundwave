from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import os
import subprocess

app = Flask(__name__)
CAPTION_FILE = "./caption.txt"
is_recording = False

if not os.path.exists(CAPTION_FILE):
    with open(CAPTION_FILE, "w") as clipboard:
        pass


@app.route('/')
def index():
    return render_template('index.html', is_recording=is_recording)


@app.route('/start-recording', methods=['POST'])
def start_recording():
    try:
        subprocess.run(["python3", "scripts/producer.py"])
        return jsonify({"status": "success", "message": "Recording started."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    try:
        subprocess.run(["pkill", "-f", "producer.py"])
        return jsonify({"status": "success", "message": "Recording stopped."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
