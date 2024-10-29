from confluent_kafka import Consumer, KafkaError
import wave
import os

# Kafka configuration
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "raw_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
OUTPUT_FILENAME = "received_audio.wav"

def consume_audio(
    topic=KAFKA_TOPIC,
    kafka_server=KAFKA_SERVER,
    output_filename=OUTPUT_FILENAME,
    sample_rate=SAMPLE_RATE,
    channels=CHANNELS,
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

    # Consume audio data from Kafka
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        print("Consuming audio data... Press Ctrl+C to stop.")
        try:
            while True:
                msg = consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print("End of partition reached")
                    else:
                        print("Error:", msg.error())
                    continue

                # Write audio chunk to the WAV file
                wf.writeframes(msg.value())

        except KeyboardInterrupt:
            print("Stopping consumer...")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")

        finally:
            wf.close()
            consumer.close()

    print(f"Recording received and saved to: {output_filename}")


if __name__ == "__main__":
    consume_audio()
