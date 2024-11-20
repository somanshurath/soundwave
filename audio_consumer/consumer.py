import socket
import os
import configparser
from confluent_kafka import Consumer, KafkaError
import time

# Load configuration from properties file
config = configparser.ConfigParser()
config.read("./metadata.properties")

KAFKA_SERVER = config.get("consumer", "bootstrap.servers")
KAFKA_TOPIC = config.get("consumer", "topic")
STORAGE_SERVERS = config.get("metadata", "storage.servers").split(",")  # Format: "ip1:port1,ip2:port2,..."
NUM_STORAGE_SERVERS = len(STORAGE_SERVERS)
GROUP_ID = "audio_consumer_group"

# Initialize Kafka consumer
consumer = Consumer({
    "bootstrap.servers": KAFKA_SERVER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
})

consumer.subscribe([KAFKA_TOPIC])

# Round-robin logic for selecting primary and backup storage servers
def get_next_servers(file_name):
    """Return the next pair of (primary, backup) storage servers based on round-robin"""
    hash_val = hash(file_name) % NUM_STORAGE_SERVERS
    primary_server = STORAGE_SERVERS[hash_val]
    backup_server = STORAGE_SERVERS[(hash_val + 1) % NUM_STORAGE_SERVERS]
    return primary_server, backup_server

def send_data_to_server(server, filename, data):
    """Send data to the specified storage server to store or append to the file."""
    try:
        host, port = server.split(":")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, int(port)))
            # Send the instruction to store or append the data
            instruction = f"STORE {filename} {data}"
            s.sendall(instruction.encode())
            response = s.recv(1024)
            return response.decode()  # Return the response from the storage server
    except Exception as e:
        print(f"Error sending data to {server}: {e}")
        return None

def consume_audio():
    print("Started consuming audio data from Kafka.")
    try:
        while True:
            msg = consumer.poll(1.0)  # Timeout of 1 second to fetch message
            if msg is None:
                continue  # No new messages

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached: {msg.partition}")
                else:
                    print(f"Error: {msg.error()}")
                continue

            # Get the filename and data
            audio_data = msg.value()
            filename = msg.key().decode()  # Assuming key in Kafka is the filename

            # Get the next round-robin pair of servers (primary and backup)
            primary_server, backup_server = get_next_servers(filename)

            # Send data to primary server
            print(f"Storing {filename} on primary server: {primary_server}")
            response = send_data_to_server(primary_server, filename, audio_data)
            if response != "SUCCESS":
                print(f"Error storing {filename} on primary server")
                continue

            # Send data to backup server
            print(f"Storing {filename} on backup server: {backup_server}")
            response = send_data_to_server(backup_server, filename, audio_data)
            if response != "SUCCESS":
                print(f"Error storing {filename} on backup server")
                continue

            print(f"Successfully stored {filename} on both primary and backup servers.")

    except KeyboardInterrupt:
        print("Stopping the consumer.")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_audio()
