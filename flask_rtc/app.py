from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os

app = Flask(__name__)
CAPTION_FILE = "./caption.txt"

if not os.path.exists(CAPTION_FILE):
    with open(CAPTION_FILE, "w") as clipboard:
        pass


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)