# Audio Consumer

This directory contains a kafka consumer python script that consumes raw audio data from a Kafka topic and saves it as a WAV file.

## Configuration

The configuration for the consumer is stored in a `consumer.properties` file. Below is an example configuration:

```properties
[consumer]
bootstrap.servers=10.70.14.81:9092
topic=raw_audio
sample.rate=44100
channels=2
chunk.size=1024
output.filename=raw_audio.wav
idle.timeout=5
```

## Usage

1. Ensure you have a Kafka server running and accessible at the address specified in the `consumer.properties` file.
2. Install the required Python packages:
    ```sh
    pip install confluent_kafka sounddevice configparser
    ```
3. Run the audio consumer script:
    ```sh
    python3 consumer.py
    ```


## Files

- `consumer.properties`: Configuration file for the Kafka consumer.
- `consumer.py`: Main script to consume audio data from Kafka and save it as a WAV file.

## How It Works

- The script reads configuration from `consumer.properties`.
- It checks if the Kafka server is available.
- It initializes a Kafka consumer.
- It consumes audio data from the specified Kafka topic.
- It saves the consumed audio data as a WAV file.
- The consumer will stop after a specified idle timeout if no messages are received.

## Note

- The consumer will stop after a specified idle timeout if no messages are received.
- The consumer will save the audio data as a WAV file with the specified filename.
- The consumer will overwrite the existing file if it already exists.


## Dependencies

- `confluent_kafka`
- `sounddevice`
- `configparser`

<br>
Back to [main readme](../README.md).