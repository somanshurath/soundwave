import sounddevice as sd
import numpy as np
from kafka import KafkaProducer
import wave
import time

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'audio2kafka'

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

SAMPLE_RATE = 44100  # Hz
DURATION = 10  # seconds per chunk

def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_data = indata.tobytes()
    key = b'audio_key'
    producer.send(TOPIC, key=key, value=audio_data)

with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
    print("Recording and streaming audio to Kafka...")
    sd.sleep(int(DURATION * 1000))
