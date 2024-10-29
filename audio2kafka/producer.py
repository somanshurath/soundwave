import sounddevice as sd
from confluent_kafka import Producer
import time

# Kafka configuration
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "raw_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK_SIZE = 1024
MAX_DURATION = 30


def delivery_report(err, msg, num):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(
            f"Message (Chunk {num}) delivered to {msg.topic()} [{msg.partition()}]")


def produce_audio(
    topic=KAFKA_TOPIC,
    kafka_server=KAFKA_SERVER,
    sample_rate=SAMPLE_RATE,
    channels=CHANNELS,
    duration=MAX_DURATION,
    chunk_size=CHUNK_SIZE,
):
    producer = Producer({"bootstrap.servers": kafka_server})

    print("Recording audio data... Press Ctrl+C to stop.")
    try:
        audio = sd.rec(
            int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype="int16"
        )
        sd.wait()
    except KeyboardInterrupt:
        print("Stopping producer...")
    except Exception as e:
        print(f"An error occurred during recording: {e}")

    # Stream audio data to Kafka in chunks
    audio_bytes = audio.tobytes()
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i: i + chunk_size]
        try:
            producer.produce(topic, value=chunk, callback=delivery_report(
                num=(i // chunk_size + 1)))
            producer.poll(0)
            time.sleep(0.01)
        except BufferError as e:
            print(f"Producer buffer full, retrying: {e}")
            producer.poll(1)
        except Exception as e:
            print(f"Error while producing message to Kafka: {e}")

    try:
        producer.flush()
        print("Recording sent to Kafka topic:", topic)
    except Exception as e:
        print(f"Error while flushing producer: {e}")


if __name__ == "__main__":
    produce_audio()
