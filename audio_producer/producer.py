from confluent_kafka import Producer
import sounddevice as sd
import time
import socket
import threading
import sys
import configparser

config = configparser.ConfigParser()
config.read('./producer.properties')

KAFKA_SERVER = config.get('producer', 'bootstrap.servers')
KAFKA_TOPIC = config.get('producer', 'topic')
SAMPLE_RATE = config.getint('producer', 'sample.rate')
CHANNELS = config.getint('producer', 'channels')
CHUNK_SIZE = config.getint('producer', 'chunk.size')


def spinner():
    spinner_frames = ["|", "/", "-", "\\"]
    idx = 0
    while True:
        sys.stdout.write(
            "\r" + spinner_frames[idx % len(spinner_frames)] + " Recording audio data...")
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


# Initialize the Kafka producer
producer = Producer({"bootstrap.servers": KAFKA_SERVER})


def delivery_report(err, num):
    if err is not None:
        print(f"Message delivery failed: {err}")


# Global variable to keep track of the number of chunks sent
chunk_counter = 0


def audio_callback(indata, frames, time_info, status):
    global chunk_counter
    if status:
        print(status)
    # Convert the audio chunk to bytes
    chunk = indata.tobytes()

    try:
        # Send the chunk to Kafka
        producer.produce(
            KAFKA_TOPIC,
            value=chunk,
            callback=lambda err, _: delivery_report(err, chunk_counter),
        )
        chunk_counter += 1
        producer.poll(0)  # Non-blocking poll to serve delivery reports
    except BufferError as e:
        print(f"\nProducer buffer full, retrying: {e}\n")
        producer.poll(1)  # Blocking poll until buffer has space


def produce_audio_realtime():
    print("Press Ctrl+C to stop recording audio data")

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.daemon = True
    spinner_thread.start()

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


if __name__ == "__main__":
    produce_audio_realtime()
