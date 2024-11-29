from confluent_kafka import Consumer, KafkaError
import sounddevice as sd
import wave
import time
import socket
import threading
import sys
import configparser

config = configparser.ConfigParser()
config.read("./consumer.properties")

KAFKA_SERVER = config.get("consumer", "bootstrap.servers")
KAFKA_TOPIC = config.get("consumer", "topic")
OUTPUT_FILENAME = config.get("consumer", "output.filename")
SAMPLE_RATE = config.getint("consumer", "sample.rate")
CHANNELS = config.getint("consumer", "channels")
IDLE_TIMEOUT = config.getint("consumer", "idle.timeout")


def spinner():
    spinner_frames = ["|", "/", "-", "\\"]
    idx = 0
    while True:
        sys.stdout.write(
            "\r"
            + spinner_frames[idx % len(spinner_frames)]
            + " Consuming caption data..."
        )
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)


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

    def consume_text(
        topic=KAFKA_TOPIC,
        kafka_server=KAFKA_SERVER,
        output_filename=OUTPUT_FILENAME,
        idle_timeout=IDLE_TIMEOUT,
    ):
        consumer = Consumer(
            {
                "bootstrap.servers": kafka_server,
                "group.id": "text_consumer_group",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,  # Auto commit offsets (for now)
            }
        )

        try:
            consumer.subscribe([topic])
        except Exception as e:
            print(
                f"An error occurred while subscribing to the topic {topic}: {e}")
            exit(1)

        # Open the file to write the received text data
        with open(output_filename, "w", encoding="utf-8") as f:
            last_message_time = time.time()

            print("Press Ctrl+C to stop consuming text data")

            spinner_thread = threading.Thread(target=spinner)
            spinner_thread.daemon = True
            spinner_thread.start()

            try:
                while True:
                    if time.time() - last_message_time > idle_timeout:
                        print(
                            f"\nNo messages received for {idle_timeout} seconds. Closing consumer"
                        )
                        break

                    msg = consumer.poll(1.0)

                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            print("\nKafka error: end of partition")
                        elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                            print(
                                "\nKafka error: unknown topic or partition. Exiting.")
                            exit(1)
                        else:
                            print("\nKafka error: ", msg.error().str())
                            exit(1)
                        continue

                    last_message_time = time.time()
                    text_chunk = msg.value().decode("utf-8")
                    f.write(text_chunk + " ")

            except KeyboardInterrupt:
                print("\nInterrupt raised. Closing consumer...")
            finally:
                consumer.close()

        print(f"Text data received and saved to: {output_filename}")

if __name__ == "__main__":
    consume_text()
