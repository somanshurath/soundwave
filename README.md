# SoundWave [⚒️ Work in Progress]

## Real-Time Audio Processing and Speech-to-Text with Kafka and Flink

### Overview
SoundWave is a real-time audio processing pipeline that ingests audio streams from multiple sources, performs audio processing tasks (including noise reduction, speech-to-text conversion, and signal mixing), and stores the processed, compressed audio along with a text transcript. Built using Apache Kafka and Apache Flink, SoundWave is optimized for fault tolerance, data redundancy, and efficient storage, using a distributed setup across three laptops.

<hr>

### Table of Contents

1. [Project Features](README#project-features)
2. [Kafka Setup](README#kafka-setup)
3. [Flink Setup](README#flink-setup)




### Project Features
- Real-Time Audio Ingestion: Captures audio streams from multiple sources.
- Stream Processing: Leverages Kafka for message brokering and Flink for real-time data transformations.
- Speech-to-Text: Converts audio streams to text transcripts.
- Noise Reduction: Enhances audio quality by filtering background noise.
- Signal Mixing: Merges audio from multiple producers into a unified stream.
- Data Redundancy: Ensures reliable data storage with backup and fault tolerance.

### Kafka Setup

download the latest kafka release and extract it from here [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.8.1/kafka_2.13-3.8.1.tgz) <br>
``` bash
tar -xzf kafka_2.13-3.8.1.tgz
cd kafka_2.13-3.8.1
```
run the following commands in separate sessions in order to start all services in the correct order:

``` bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties	
```
now, your kafka server is up and running.

### Flink Setup
(tbd)
