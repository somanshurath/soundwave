from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaRecordSerializationSchema
from pyflink.datastream.connectors.kafka import (
    KafkaOffsetsInitializer,
    KafkaSink,
    KafkaSource,
)
from pyflink.common.serialization import DeserializationSchema, SerializationSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.data_stream import WatermarkStrategy
from pyflink.java_gateway import get_gateway
import io
import librosa
import numpy as np
import soundfile as sf
import configparser

config = configparser.ConfigParser()
config.read("./flink.properties")

KAFKA_SERVER = "localhost:9092"
RAW_AUDIO_TOPIC = "raw_audio"
PROCESSED_AUDIO_TOPIC = "librosa_audio"
SAMPLE_RATE = 44100
CHANNELS = 2
SEMITONES = 2
BUFFER_SIZE = SAMPLE_RATE * CHANNELS * 2  # The threshold for enough data to process
FLINK_SQL_CONNECTOR_JAR = config.get("flink", "flink.sql.connector.jar")
FLINK_BYTE_ARRAY_SERDE_JAR = config.get("flink", "flink.byte.array.serde.jar")


# ByteArray Deserializer
class ByteArrayDeserializer(DeserializationSchema):
    def __init__(self):
        gate_way = get_gateway()
        j_byte_array_schema = gate_way.jvm.com.example.serdes.ByteArrayDeserializer()
        DeserializationSchema.__init__(
            self, j_deserialization_schema=j_byte_array_schema
        )

    def deserialize(self, message):
        return message

    def is_end_of_stream(self, message):
        return False

    def get_produced_type(self):
        return Types.PRIMITIVE_ARRAY(Types.BYTE())


# ByteArray Serializer
class ByteArraySerializer(SerializationSchema):
    def __init__(self):
        gate_way = get_gateway()
        j_byte_array_schema = gate_way.jvm.com.example.serdes.ByteArraySerializer()
        SerializationSchema.__init__(self, j_serialization_schema=j_byte_array_schema)

    def serialize(self, element):
        return element


# Audio Processing Function to raise pitch
def raise_pitch(audio_chunk, sample_rate=SAMPLE_RATE, semitones=SEMITONES):
    y = np.frombuffer(audio_chunk, dtype=np.int16)
    y = y.astype(np.float32) / 32768.0
    n_fft = 256
    y_shifted = librosa.effects.pitch_shift(
        y, sr=sample_rate, n_steps=semitones, n_fft=n_fft
    )
    y_shifted = np.int16(y_shifted * 32768)
    output = io.BytesIO()
    sf.write(output, y_shifted, sample_rate, format="WAV")
    return output.getvalue()


# audio processing function
def process_audio(audio_chunk):
    return raise_pitch(audio_chunk)


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(
        FLINK_SQL_CONNECTOR_JAR,
        FLINK_BYTE_ARRAY_SERDE_JAR,
    )

    # Set up Kafka consumer
    kafka_consumer = (
        KafkaSource.builder()
        .set_topics(RAW_AUDIO_TOPIC)
        .set_bootstrap_servers(KAFKA_SERVER)
        .set_group_id("flink_consumer")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(ByteArrayDeserializer())
        .build()
    )

    # Set up Kafka producer
    kafka_producer = (
        KafkaSink.builder()
        .set_bootstrap_servers(KAFKA_SERVER)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(PROCESSED_AUDIO_TOPIC)
            .set_value_serialization_schema(ByteArraySerializer())
            .build()
        )
        .build()
    )

    # Stream processing with the audio processor
    audio_stream = env.from_source(
        kafka_consumer, WatermarkStrategy.no_watermarks(), "Kafka Source"
    )

    # Further processing with Python function
    processed_stream = audio_stream.map(
        process_audio, output_type=Types.PRIMITIVE_ARRAY(Types.BYTE())
    )

    # Output to Kafka (or any other sink)
    processed_stream.sink_to(kafka_producer)

    # Execute the Flink job
    env.execute("Kafka Audio Stream Processing")


if __name__ == "__main__":
    main()
