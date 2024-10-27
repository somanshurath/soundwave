from kafka import KafkaConsumer
import numpy as np
import sounddevice as sd
import wave

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'audio2kafka'

SAMPLE_RATE = 44100  # Hz
CHANNELS = 1  # Mono audio

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

def save_audio(data, filename='received_audio.wav'):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 2 bytes for int16 format
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(data)

audio_data = b''
print("Consuming and playing audio...")

for message in consumer:
    audio_chunk = message.value
    audio_data += audio_chunk

    audio_array = np.frombuffer(audio_chunk, dtype=np.int16)

    sd.play(audio_array, samplerate=SAMPLE_RATE)
    sd.wait()

    if len(audio_data) >= SAMPLE_RATE * 2 * 10:
        break

save_audio(audio_data, 'records/received_audio.wav')
print("Audio saved to received_audio.wav")
