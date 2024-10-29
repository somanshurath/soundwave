import time
from confluent_kafka import Consumer, KafkaError
import wave
import sounddevice as sd

# Kafka configuration
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "raw_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
OUTPUT_FILENAME = "received_audio.wav"
IDLE_TIMEOUT = 10  # Time in seconds to wait before closing if no messages are received


def consume_audio(
    topic=KAFKA_TOPIC,
    kafka_server=KAFKA_SERVER,
    output_filename=OUTPUT_FILENAME,
    sample_rate=SAMPLE_RATE,
    channels=CHANNELS,
    idle_timeout=IDLE_TIMEOUT,
):
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_server,
            "group.id": "raw_audio_consumer_group",
            "auto.offset.reset": "earliest",
        }
    )

    try:
        consumer.subscribe([topic])
    except Exception as e:
        print(f"An error occurred while subscribing to the topic {topic}: {e}")

    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        last_message_time = time.time()
        print("Consuming audio data... Press Ctrl+C to stop.")

        try:
            while True:
                # Check if idle timeout has been reached
                if time.time() - last_message_time > idle_timeout:
                    print(
                        f"No messages received for {idle_timeout} seconds. Closing consumer."
                    )
                    break

                msg = consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print("End of partition reached")
                    else:
                        print("Error:", msg.error())
                    continue

                # Update last message time since a message was received
                last_message_time = time.time()

                # Write audio chunk to the WAV file
                audio_chunk = msg.value()
                wf.writeframes(audio_chunk)

        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            consumer.close()

    print(f"Recording received and saved to: {output_filename}")


if __name__ == "__main__":
    consume_audio()
