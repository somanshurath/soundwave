import sounddevice as sd
from confluent_kafka import Producer
import time

# Kafka configuration
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "raw_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK_SIZE = 1024

# Initialize the Kafka producer
producer = Producer({"bootstrap.servers": KAFKA_SERVER})


def delivery_report(err, msg, num):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message (Chunk {num}) delivered to {msg.topic()} [{msg.partition()}]")


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
            callback=lambda err, msg: delivery_report(err, msg, chunk_counter),
        )
        chunk_counter += 1
        producer.poll(0)  # Non-blocking poll to serve delivery reports
    except BufferError as e:
        print(f"Producer buffer full, retrying: {e}")
        producer.poll(1)  # Blocking poll until buffer has space


def produce_audio_realtime():
    print("Recording audio in real-time... Press Ctrl+C to stop.")
    try:
        # Start streaming audio in real-time
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=audio_callback,
        ):
            # Keep the stream open until interrupted
            while True:
                time.sleep(0.1)  # Sleep to keep the main thread alive
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        try:
            producer.flush()
            print("Remaining messages flushed to Kafka.")
        except Exception as e:
            print(f"Error while flushing producer: {e}")


if __name__ == "__main__":
    produce_audio_realtime()
