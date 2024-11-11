from confluent_kafka import Consumer, Producer, KafkaError
import io
import librosa
import numpy as np
import socket
import soundfile as sf

# Kafka configuration
KAFKA_SERVER = "localhost:9092"
RAW_AUDIO_TOPIC = "raw_audio"
PROCESSED_AUDIO_TOPIC = "librosa_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
CHUNK_SIZE = 1024


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


def raise_pitch(audio_chunk, sample_rate=SAMPLE_RATE, semitones=2):
    y = np.frombuffer(audio_chunk, dtype=np.int16)
    y = y.astype(np.float32) / 32768.0

    y_shifted = librosa.effects.pitch_shift(
        y, sr=sample_rate, n_steps=semitones)

    y_shifted = np.int16(y_shifted * 32768)

    output = io.BytesIO()
    sf.write(output, y_shifted, sample_rate, format='WAV')
    output.seek(0)
    return output.read()


def stream_process_audio():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_SERVER,
        "group.id": "audio_processing_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    producer = Producer({"bootstrap.servers": KAFKA_SERVER})

    try:
        consumer.subscribe([RAW_AUDIO_TOPIC])
    except Exception as e:
        print(
            f"An error occurred while subscribing to the topic {RAW_AUDIO_TOPIC}: {e}")
        exit(1)

    try:
        print("Streaming audio data. Press Ctrl+C to stop.")
        audio_buffer = bytearray()
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print("End of partition reached.")
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print("Error: Unknown topic or partition.")
                    exit(1)
                else:
                    print(f"Error: {msg.error()}")
                    exit(1)
                continue

            audio_data = msg.value()
            audio_buffer.extend(audio_data)

            if len(audio_buffer) >= SAMPLE_RATE * CHANNELS * 2:
                pitched_chunk = raise_pitch(audio_buffer)

                audio_buffer = bytearray()
                producer.produce(PROCESSED_AUDIO_TOPIC, pitched_chunk)
                producer.flush()

    except KeyboardInterrupt:
        print("Streaming stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":
    stream_process_audio()
