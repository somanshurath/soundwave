from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import DeserializationSchema, SerializationSchema
from pyflink.common.typeinfo import Types
import io
import librosa
import numpy as np
import soundfile as sf

# Configuration
KAFKA_SERVER = "localhost:9092"
RAW_AUDIO_TOPIC = "raw_audio"
PROCESSED_AUDIO_TOPIC = "librosa_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
SEMITONES = 2


# Custom Deserialization Schema for Byte Arrays
class ByteArrayDeserializationSchema(DeserializationSchema):
    def deserialize(self, message):
        return message  # Return as-is for raw byte array

    def is_end_of_stream(self, message):
        return False

    def get_produced_type(self):
        return Types.PRIMITIVE_ARRAY(Types.BYTE())


# Custom Serialization Schema for Byte Arrays
class ByteArraySerializationSchema(SerializationSchema):
    def serialize(self, element):
        return element  # Return as-is for raw byte array


def raise_pitch(audio_chunk, sample_rate=SAMPLE_RATE, semitones=SEMITONES):
    y = np.frombuffer(audio_chunk, dtype=np.int16)
    y = y.astype(np.float32) / 32768.0
    y_shifted = librosa.effects.pitch_shift(y, sr=sample_rate, n_steps=semitones)
    y_shifted = np.int16(y_shifted * 32768)
    output = io.BytesIO()
    sf.write(output, y_shifted, sample_rate, format="WAV")
    return output.getvalue()


def audio_processing_function(value):
    pitched_audio = raise_pitch(value)
    return pitched_audio


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(
        "file:///home/lordminion666/.m2/repository/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar"
    )
    # Set up Kafka consumer with custom deserialization schema
    kafka_consumer = FlinkKafkaConsumer(
        topics=RAW_AUDIO_TOPIC,
        deserialization_schema=ByteArrayDeserializationSchema(),
        properties={
            "bootstrap.servers": KAFKA_SERVER,
            "group.id": "audio_processing_group",
        },
    )

    # Set up Kafka producer with custom serialization schema
    kafka_producer = FlinkKafkaProducer(
        topic=PROCESSED_AUDIO_TOPIC,
        serialization_schema=ByteArraySerializationSchema(),
        producer_config={"bootstrap.servers": KAFKA_SERVER},
    )

    # Stream processing
    audio_stream = env.add_source(kafka_consumer)
    processed_stream = audio_stream.map(
        audio_processing_function, output_type=Types.PRIMITIVE_ARRAY(Types.BYTE())
    )  # Use PICKLED_BYTE_ARRAY
    processed_stream.add_sink(kafka_producer)

    # Execute the Flink job
    env.execute("Kafka Audio Stream Processing")


if __name__ == "__main__":
    main()
