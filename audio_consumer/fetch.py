import os
import subprocess
from flask import Flask, request, send_file, jsonify, abort

app = Flask(__name__)

# List of GlusterFS storage containers to check
STORAGE_SERVERS = ["glusterfs1", "glusterfs2", "glusterfs3"]

# Base path for file storage in containers
FILE_PATH = "/gluster/brick/data/"

def is_server_running(server_name):
    """
    Check if a Docker container is running using docker inspect.
    """
    try:
        result = subprocess.run(
            ["sudo", "docker", "inspect", "-f", "{{.State.Running}}", server_name],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().lower() == "true"
    except subprocess.CalledProcessError:
        return False

def is_file_present(server_name, filename):
    """
    Check if a file exists inside the given Docker container.
    """
    try:
        subprocess.run(
            ["sudo", "docker", "exec", server_name, "ls", f"{FILE_PATH}{filename}"],
            capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    
@app.route('/get_file_list', methods=['GET'])
def get_file_list():
    """
    Endpoint to fetch a list of files from the storage servers.
    """
    files = []
    for server in STORAGE_SERVERS:
        if is_server_running(server):
            app.logger.info(f"{server} is online checking for files")
            try:
                result = subprocess.run(
                    ["sudo", "docker", "exec", server, "ls", FILE_PATH],
                    capture_output=True, text=True, check=True
                )
                files.extend(result.stdout.strip().split("\n"))
            except subprocess.CalledProcessError:
                app.logger.error(f"Failed to get files from {server}")
        else:
            app.logger.info(f"{server} is not running.")

    return jsonify({"files": files})

@app.route('/get_file', methods=['GET'])
def get_file():
    """
    Endpoint to fetch a file from the storage servers.
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    for server in STORAGE_SERVERS:
        if is_server_running(server):
            print(f"{server} is online checking for {filename}")
            if is_file_present(server, filename):
                print(f"Found {filename} and sending now")
                try:
                    return send_file(local_file_path, as_attachment=True)
                except:
                    return jsonify({"error": "Failed to retrieve file"}), 500
        else:
            app.logger.info(f"{server} is not running.")

    return jsonify({"error": "File not found on any active server"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
