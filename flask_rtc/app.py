from flask import Flask, render_template, request, jsonify
import os
import subprocess

app = Flask(__name__)
CAPTION_FILE = "./scripts/captions.txt"

if not os.path.exists(CAPTION_FILE):
    with open(CAPTION_FILE, "w") as clipboard:
        pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-caption', methods=['GET'])
def get_caption():
    caption_text = ""
    if os.path.exists(CAPTION_FILE):
        with open(CAPTION_FILE, "r") as f:
            caption_text = f.read()
    return jsonify({"caption_text": caption_text})


@app.route('/start-recording', methods=['POST'])
def start_recording():
    try:
        subprocess.Popen(["python3", "scripts/producer.py"])
        return jsonify({"status": "success", "message": "Recording started."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    try:
        subprocess.Popen(["pkill", "-2", "-f", "producer.py"])
        # delete the caption file content
        # with open(CAPTION_FILE, "w") as clipboard:
        #     clipboard.truncate(0)
        return jsonify({"status": "success", "message": "Recording stopped."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
