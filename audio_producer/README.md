# Audio Producer

This directory contains a audio producer python script captures real-time audio data and sends it to a Kafka topic.

## Configuration

The configuration for the producer is stored in a `producer.properties` file. Below is an example configuration:

```properties
[producer]
bootstrap.servers=10.70.14.81:9092
topic=raw_audio
sample.rate=44100
channels=2
chunk.size=1024
```

## Usage

1. Ensure you have a Kafka server running and accessible at the address specified in the `producer.properties` file.
2. Install the required Python packages:
    ```sh
    pip install confluent_kafka sounddevice configparser
    ```
3. Run the audio producer script:
    ```sh
    python3 producer.py
    ```

## Files

- `producer.properties`: Configuration file for the Kafka producer.
- `producer.py`: Main script to capture audio and send it to Kafka.

## How It Works

- The script reads configuration from `producer.properties`.
- It checks if the Kafka server is available.
- It initializes a Kafka producer.
- It captures audio data in real-time using the `sounddevice` library.
- It sends the captured audio data to the specified Kafka topic.

Press `Ctrl+C` to stop the audio recording and gracefully shut down the producer.

## Dependencies

- `confluent_kafka`
- `sounddevice`
- `configparser`

<br>
Back to [main readme](../README.md).