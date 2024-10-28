import sounddevice as sd
from confluent_kafka import Producer
import time


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def record_audio_and_send(
    duration=5,
    sample_rate=44100,
    topic="audio_topic",
    kafka_server="localhost:9092",
    chunk_size=1024,
):
    producer = Producer({"bootstrap.servers": kafka_server})

    print("Recording...")
    audio = sd.rec(
        int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype="int16"
    )
    sd.wait()

    # Send in chunks
    audio_bytes = audio.tobytes()
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i : i + chunk_size]
        producer.produce(topic, value=chunk, callback=delivery_report)
        producer.poll(0)
        time.sleep(0.01)

    producer.flush()
    print("Recording sent to Kafka topic:", topic)


# Record and send a 5-second audio file
record_audio_and_send()
