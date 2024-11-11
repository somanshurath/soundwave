
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.util.serialization.DeserializationSchema;

import org.apache.flink.api.common.serialization.SerializationSchema;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.streaming.api.functions.ProcessFunction;

import java.util.Properties;
import javax.sound.sampled.*;

import com.github.psambit9791.jdsp.pitch.PitchShift;

public class FlinkAudioProcessing {
    
    private static final String KAFKA_SERVER = "localhost:9092";
    private static final String RAW_AUDIO_TOPIC = "raw_audio";
    private static final String PROCESSED_AUDIO_TOPIC = "librosa_audio";
    private static final int SAMPLE_RATE = 44100;
    private static final int CHANNELS = 2;
    private static final int CHUNK_SIZE = 1024;
    
    public static void main(String[] args) throws Exception {
        // Set up the Flink environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Kafka Consumer configuration
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, KAFKA_SERVER);
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "audio_processing_group");
        
        FlinkKafkaConsumer<byte[]> consumer = new FlinkKafkaConsumer<>(
                RAW_AUDIO_TOPIC,
                new AudioDeserializer(),
                consumerProps
        );
        
        // Create Flink data stream
        DataStream<byte[]> audioStream = env.addSource(consumer);
        
        // Apply audio processing (pitch shifting)
        DataStream<byte[]> processedAudioStream = audioStream.map(new PitchShiftFunction());
        
        // Kafka Producer configuration
        Properties producerProps = new Properties();
        producerProps.put("bootstrap.servers", KAFKA_SERVER);
        
        FlinkKafkaProducer<byte[]> producer = new FlinkKafkaProducer<>(
                PROCESSED_AUDIO_TOPIC,
                new AudioSerializationSchema(),
                producerProps,
                FlinkKafkaProducer.Semantic.EXACTLY_ONCE
        );
        
        // Write processed audio to Kafka topic
        processedAudioStream.addSink(producer);
        
        // Execute the Flink job
        env.execute("Flink Audio Processing");
    }
    
    // Deserializer for raw audio data from Kafka
    public static class AudioDeserializer implements DeserializationSchema<byte[]> {
        @Override
        public byte[] deserialize(byte[] message) {
            return message;
        }

        @Override
        public boolean isEndOfStream(byte[] nextElement) {
            return false;
        }

        @Override
        public TypeInformation<byte[]> getProducedType() {
            return TypeInformation.of(byte[].class);
        }
    }

    // Serializer for processed audio data to Kafka
    public static class AudioSerializationSchema implements SerializationSchema<byte[]> {
        @Override
        public byte[] serialize(byte[] element) {
            return element;
        }
    }

    // Map function to perform pitch shift
    public static class PitchShiftFunction implements MapFunction<byte[], byte[]> {
        @Override
        public byte[] map(byte[] audioData) throws Exception {
            // Convert the byte array to audio (16-bit signed PCM format)
            AudioFormat format = new AudioFormat(SAMPLE_RATE, 16, CHANNELS, true, false);
            AudioInputStream audioStream = new AudioInputStream(new ByteArrayInputStream(audioData), format, audioData.length);
            
            // Process pitch shift using TarsosDSP
            byte[] shiftedAudio = pitchShift(audioData, SAMPLE_RATE, 2); // Pitch shift by 2 semitones

            return shiftedAudio;
        }

        // Method for pitch shifting using TarsosDSP
        public byte[] pitchShift(byte[] audioData, int sampleRate, int semitones) {
            try {
                // Initialize pitch shift process
                PitchShift pitchShift = new PitchShift(sampleRate);
                float[] audioFloats = new float[audioData.length / 2];
                
                // Convert byte array to float array
                for (int i = 0; i < audioFloats.length; i++) {
                    audioFloats[i] = ((short) (audioData[i * 2] << 8 | (audioData[i * 2 + 1] & 0xFF))) / 32768f;
                }

                // Perform pitch shift
                float[] shifted = pitchShift.shift(audioFloats, semitones);

                // Convert the float array back to byte array
                byte[] shiftedAudio = new byte[shifted.length * 2];
                for (int i = 0; i < shifted.length; i++) {
                    short sample = (short) (shifted[i] * 32768);
                    shiftedAudio[i * 2] = (byte) (sample >> 8);
                    shiftedAudio[i * 2 + 1] = (byte) (sample & 0xFF);
                }

                return shiftedAudio;
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }
    }
}
