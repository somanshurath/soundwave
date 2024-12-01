from flask import Flask, send_from_directory, render_template, request, jsonify
import os
import json
import requests
import subprocess
import wave
from scripts.speech_to_text import speech_to_text

app = Flask(__name__)
DOWNLOAD_FOLDER = './downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

raw = "raw_audio.wav"


@app.route('/')
def index():
    files = []
    try:
        result = subprocess.run(
            ["curl", "http://192.168.20.55:5000/get_file_list"],
            capture_output=True, text=True, check=True
        )
        filesData = result.stdout.strip().split("\n")
        filesData = ''.join(filesData)  # Join the list into a single string
        filesD = json.loads(filesData)
        files = filesD.get("files")
        return render_template("index.html", files=files, raw=raw)
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)})


# This route will download the file from the remote laptop and save it locally
@app.route('/download-audio/<filename>', methods=['GET'])
def download_file(filename):
    # URL of the server where the file is located
    remote_url = f'http://192.168.20.55:5000/get_file?filename={filename}'

    # Send the GET request to the remote server to fetch the file
    try:
        result = subprocess.run(
            ["curl", "-L", remote_url],  # Added -L to follow redirects if needed
            capture_output=True,
            text=False,  # Capture binary output (not text)
            check=True
        )
        # Write the binary content to a file
        with wave.open(f"downloads/{filename}", "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(result.stdout)

        return jsonify({"status": "success", "message": "File downloaded successfully"})

    except subprocess.CalledProcessError as e:
        # Catch network or connection errors
        print(f'An error occurred: {str(e)}')
        return jsonify({"status": "error", "message": str(e)})


# This route will download the file from the remote laptop and save it locally
@app.route('/transcribe-audio/<filename>', methods=['GET'])
def transcribe_file(filename):

    text = speech_to_text(f"downloads/{filename}")
    # save as txt in downloads folder
    with open(f"downloads/{filename}.txt", "w") as f:
        f.write(text)
    return jsonify({"status": "success", "message": "File transcribed successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6060)
