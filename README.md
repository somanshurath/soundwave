<h1 style="text-align: center; display: flex; justify-content: center; align-items: center;">
  <img src="assets/audio-waves.png" width="50px" alt="Audio Waves Icon" style="margin-right: 10px;"/>
  SoundWave
</h1>


<!-- https://somanshurath.github.io/soundwave/ <br> -->
Real-Time Audio Processing and Speech-to-Text with Kafka and Flink

## Table of Contents

1. [Project Overview](README#project-overview)
2. [Architecture](README#architecture)
3. [Audio Processing](README#audio-processing)
    - [Kafka Setup](README#kafka-setup)
    - [Flink Setup](README#flink-setup)

## Project Overview

SoundWave is a real-time audio processing pipeline that ingests audio streams from multiple sources, performs audio processing tasks (primarily pitch shift), and stores the processed audio, which can be further processed to generate a transcript. Built using Apache Kafka, Apache Flink and GlusterFS, SoundWave is optimized for fault tolerance, data redundancy, and efficient storage, using a distributed setup to ensure scalability and reliability.

## Architecture

<img src="soundwave.svg" alt="Description of SVG" width="100%" />

## Audio Processing

### Kafka Setup

download the latest kafka release and extract it from here [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.8.1/kafka_2.13-3.8.1.tgz) <br>

```bash
tar -xzf kafka_2.13-3.8.1.tgz
cd kafka_2.13-3.8.1
```

run the following commands in separate sessions in order to start all services in the correct order:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

now, your kafka broker is up and running.

### Flink Setup

download flink sql connector jar from [here](https://mvnrepository.com/artifact/org.apache.flink/flink-sql-connector-kafka/3.3.0-1.20) and correctly replace the JAR path in `flink.properties`.<br>
