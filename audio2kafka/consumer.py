from confluent_kafka import Consumer, KafkaError
import wave


def consume_audio(
    topic="audio_topic",
    kafka_server="localhost:9092",
    output_filename="received_audio.wav",
    sample_rate=44100,
    channels=2,
):
    # Configure the consumer
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_server,
            "group.id": "audio_consumer_group",
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([topic])

    # Set up WAV file output
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)

        print("Consuming audio data... Press Ctrl+C to stop.")
        try:
            while True:
                msg = consumer.poll(1.0)  # Wait up to 1 second for a message

                if msg is None:
                    continue  # No message
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print("End of partition reached")
                    else:
                        print("Error:", msg.error())
                    continue

                # Write received audio chunk to the WAV file
                wf.writeframes(msg.value())

        except KeyboardInterrupt:
            print("Stopping consumer...")

    consumer.close()
    print(f"Audio received and saved to {output_filename}")


# Run the consumer to receive audio and save it to a file
consume_audio()
