from typing import ChainMap
from confluent_kafka import Producer
import sounddevice as sd
import time
import socket
import threading
import sys

KAFKA_SERVER = "10.30.12.77:9092"
KAFKA_TOPIC = "raw_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK_SIZE = 1024


# Function to check if the Kafka server is reachable
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

# Initialize the Kafka producer
producer = Producer({"bootstrap.servers": KAFKA_SERVER})


# Function to handle delivery reports from the producer
def delivery_report(err, num):
    if err is not None:
        print(f"Message delivery failed: {err}")


# Global variables
chunk_counter = 0
audio_buffer = bytearray()  # Buffer to accumulate audio data


# Callback function for the audio stream
def audio_callback(indata, frames, time_info, status):
    global chunk_counter, audio_buffer
    if status:
        print(status)

    # Convert the audio chunk to bytes and add to the buffer
    chunk = indata.tobytes()
    audio_buffer.extend(chunk)

    while len(audio_buffer) >= SAMPLE_RATE * CHANNELS * 2:
        try:
            producer.produce(
                KAFKA_TOPIC,
                value=bytes(audio_buffer),
                callback=lambda err, _: delivery_report(err, chunk_counter),
            )
            chunk_counter += 1
            producer.poll(0)  # Non-blocking poll to serve delivery reports

            # Remove the sent bytes from the buffer
            audio_buffer.clear()
        except BufferError as e:
            print(f"\nProducer buffer full, retrying: {e}\n")
            producer.poll(1)  # Blocking poll until buffer has space


# Main function to produce audio data in real-time
def produce_audio_realtime():
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nInterrupt raised. Stopping producer...")
    finally:
        sd.stop()
        try:
            producer.flush()
            print("\nRemaining messages flushed to Kafka cluster.\nClosing producer...")
        except Exception as e:
            print(f"\nAn error occurred in closing the producer: {e}")


# Run the program
if __name__ == "__main__":
    produce_audio_realtime()
