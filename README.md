# SoundWave [⚒️ Work in Progress]

## Real-Time Audio Processing and Speech-to-Text with Kafka and Flink

### Overview
SoundWave is a real-time audio processing pipeline that ingests audio streams from multiple sources, performs audio processing tasks (including noise reduction, speech-to-text conversion, and signal mixing), and stores the processed, compressed audio along with a text transcript. Built using Apache Kafka and Apache Flink, SoundWave is optimized for fault tolerance, data redundancy, and efficient storage, using a distributed setup across three laptops.

<hr>

### Table of Contents

1. [Project Features](README#project-features)
2. [Setup](README#Setup)




### Project Features
- Real-Time Audio Ingestion: Captures audio streams from multiple sources.
- Stream Processing: Leverages Kafka for message brokering and Flink for real-time data transformations.
- Speech-to-Text: Converts audio streams to text transcripts.
- Noise Reduction: Enhances audio quality by filtering background noise.
- Signal Mixing: Merges audio from multiple producers into a unified stream.
- Data Redundancy: Ensures reliable data storage with backup and fault tolerance.

### Setup

install kafka from (insert link) <br>
open the folder in terminal and type

```
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties	
```

**Note: KVR**

however check zookeeper.properties and server.properties. there has to be some changes for sure.
For one,
> the broker id is fixed as 0 in one of the above and in the take-home's docker-compose.yaml we had broker id as 1 however each broker is supposed to have unique id.

well update this part, once you get an idea. thanks.
