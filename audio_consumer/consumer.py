from confluent_kafka import Consumer, KafkaError
import sounddevice as sd
import wave
import time
import socket
import threading
import sys
import configparser
import sys

config = configparser.ConfigParser()
config.read("./consumer.properties")


if len(sys.argv) != 3:
    print("Usage: python script.py <output_filename>")
    sys.exit(1)

KAFKA_SERVER = config.get("consumer", "bootstrap.servers")
KAFKA_TOPIC = config.get("consumer", "topic")
OUTPUT_FILENAME = sys.argv[1]
SAMPLE_RATE = config.getint("consumer", "sample.rate")
CHANNELS = config.getint("consumer", "channels")
IDLE_TIMEOUT = config.getint("consumer", "idle.timeout")
STORAGE_SERVERS = config.get("storage.servers").split(",")  # Format: "ip1:port1,ip2:port2,..."



def get_storage_server():
	



def spinner():
    spinner_frames = ["|", "/", "-", "\\"]
    idx = 0
    while True:
        sys.stdout.write(
            "\r" + spinner_frames[idx % len(spinner_frames)] + " Consuming audio data...")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)


def check_kafka_server(server):
    host, port = server.split(":")
    try:
        socket.create_connection((host, int(port)), timeout=5)
        return True
    except (socket.timeout, ConnectionRefusedError, socket.gaierror):
        return False


# Check if Kafka server is available
if not check_kafka_server(KAFKA_SERVER):
    print(
        f"Kafka server at {KAFKA_SERVER} is not available. Please check:\n 1. Kafka server is running\n 2. Kafka server address is correct\nTry again after resolving issues."
    )
    exit(1)
else:
    print(f"Kafka server at {KAFKA_SERVER} up and running")
    
    
def send_data_to_server(server, filename, data):
    """Send data to the specified storage server to store or append to the file."""
    try:
        host, port = server.split(":")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, int(port)))
            # Send the instruction to store or append the data
            instruction = f"STORE {filename}".encode() + b' ' + data
            s.sendall(instruction)
            response = s.recv(1024)
            return response.decode()  # Return the response from the storage server
    except Exception as e:
        print(f"Error sending data to {server}: {e}")
        return None    


def consume_audio(
    topic=KAFKA_TOPIC,
    kafka_server=KAFKA_SERVER,
    output_filename=OUTPUT_FILENAME,
    sample_rate=SAMPLE_RATE,
    channels=CHANNELS,
    idle_timeout=IDLE_TIMEOUT,
):
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_server,
            "group.id": "raw_audio_consumer_group",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,  # Auto commit offsets (for now)
        }
    )

    try:
        consumer.subscribe([topic])
    except Exception as e:
        print(f"An error occurred while subscribing to the topic {topic}: {e}")
        exit(1)

    # Open the WAV file to write the received audio data
    #with wave.open(output_filename, "wb") as wf:
    #    wf.setnchannels(channels)
    #    wf.setsampwidth(2)
    #    wf.setframerate(sample_rate)
	last_message_time = time.time()

	print("Press Ctrl+C to stop consuming audio data")

	spinner_thread = threading.Thread(target=spinner)
	spinner_thread.daemon = True
	spinner_thread.start()

	try:
		while True:
		if time.time() - last_message_time > idle_timeout:
			print(
			    f"\nNo messages received for {idle_timeout} seconds. Closing consumer"
			)
			break

		msg = consumer.poll(1.0)

		if msg is None:
			continue
		if msg.error():
			if msg.error().code() == KafkaError._PARTITION_EOF:
			    print("\nKafka error: end of partition")
			elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
			    print("\nKafka error: unknown topic or partition. Exiting.")
			    exit(1)
			else:
			    print("\nKafka error: ", msg.error().str())
			    exit(1)
			continue

		last_message_time = time.time()
		audio_chunk = msg.value()
		primary_server, backup_server = STORAGE_SERVERS[0:2];

        # Send data to primary server
        print(f"Storing {filename} on primary server: {primary_server}")
        response = send_data_to_server(primary_server, output_filename, audio_chunk)
        if response != "SUCCESS":
            print(f"Error storing {filename} on primary server")
            continue

        # Send data to backup server
        print(f"Storing {filename} on backup server: {backup_server}")
        response = send_data_to_server(backup_server, ouput_filename, audio_chunk)
        if response != "SUCCESS":
            print(f"Error storing {filename} on backup server")
            continue

        print(f"Successfully stored {filename} on both primary and backup servers.")

	

	except KeyboardInterrupt:
		print("\nInterrupt raised. Closing consumer...")
	finally:
		consumer.close()

		print(f"Recording received and saved to: {output_filename}")


if __name__ == "__main__":
    consume_audio()
