from confluent_kafka import Consumer, Producer, KafkaError
import io
import librosa
import numpy as np
import socket
import soundfile as sf
import speech_recognition as sr

# Kafka configuration
KAFKA_SERVER = "10.70.24.72:9092"
RAW_AUDIO_TOPIC = "raw_audio"
CAPTIONS_TOPIC = "rtc_text"
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


def speech_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        # return "Google Speech Recognition could not understand the audio"
        return "."
    except sr.RequestError as e:
        # return f"Could not request results from Google Speech Recognition service; {e}"
        return "."
    except Exception as e:
        # return f"An error occurred during speech recognition; {e}"
        return "."


def process_audio_buffer(audio_buffer):
    audio_data = np.frombuffer(audio_buffer, dtype=np.int16)
    audio_data = audio_data.astype(np.float32) / 32768.0  # Convert to float32

    audio_data = audio_data.reshape(-1, CHANNELS)

    audio_data = np.mean(audio_data, axis=1)

    with io.BytesIO() as audio_file:
        sf.write(audio_file, audio_data, SAMPLE_RATE, format='WAV')
        audio_file.seek(0)
        text = speech_to_text(audio_file)

    return text


def stream_audio__caption():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_SERVER,
        "group.id": "audio_processing_group",
        "auto.offset.reset": "latest",
        "enable.auto.commit": True,
    })
    producer = Producer({"bootstrap.servers": KAFKA_SERVER})

    try:
        consumer.subscribe([RAW_AUDIO_TOPIC])
    except Exception as e:
        print(
            f"An error occurred while subscribing to the topic {RAW_AUDIO_TOPIC}: {e}")
        exit(1)

    try:
        print("Streaming audio captions in realtime. Press Ctrl+C to stop.")
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

            if len(audio_buffer) >= SAMPLE_RATE * CHANNELS * 5:
                caption = process_audio_buffer(audio_buffer)
                producer.produce(CAPTIONS_TOPIC, caption.encode("utf-8"))
                audio_buffer.clear()

    except KeyboardInterrupt:
        print("Streaming stopped.")
    finally:
        consumer.close()
        producer.flush()


if __name__ == "__main__":
    stream_audio__caption()
