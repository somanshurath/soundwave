import socket
import os
import wave

def handle_client_connection(client_socket):
    """Handles the connection from the metadata server."""
    try:
        # Receive the instruction from the metadata server
        request = client_socket.recv(1024)
        if not request:
            return

        # Parse the instruction
        parts = request.split(b' ', 2)
        if len(parts) < 3 or parts[0].decode() != "STORE":
            client_socket.sendall(b"ERROR: Invalid instruction")
            return

        # Extract filename and data
        filename, data = parts[1].decode(), parts[2]
        
        # Path to the file on this server
        file_path = f"/data/{filename}"

        # Check if the file exists
        file_exists = os.path.exists(file_path)
        
        # Open the file to write data (or append)
        with wave.open(file_path, 'wb') as wf:
            # Set properties (ensure these values are passed or defined)
            channels = 1           # Example value, should be set as needed
            sample_rate = 44100    # Example value, should be set as needed
            sampwidth = 2          # 16-bit sample width
            
            wf.setnchannels(channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            
            # Write the received data (audio) into the file
            wf.writeframes(data)
            client_socket.sendall(b"SUCCESS")

    except Exception as e:
        print(f"Error handling client connection: {e}")
        client_socket.sendall(b"ERROR: An error occurred")

    finally:
        client_socket.close()


def start_storage_server(host, port):
    """Starts the storage server to listen for incoming instructions."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    print(f"Storage server listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Connection received from {addr}")
            handle_client_connection(client_socket)
    except KeyboardInterrupt:
        print("\nServer interrupted by user. Shutting down...")
    finally:
        server.close()
        print("Server shut down.")


if __name__ == "__main__":
    start_storage_server("172.17.0.2", 5000)  # Adjust the IP and port as needed
