# Audio2Kafka

Preliminary setup to test the integration of audio processing with Kafka. <br>
Open this project (preferably on pycharm) and use the virtual environment to install the dependencies. <br>
Use requirements.txt to install dependencies in your virtual environment.

### Configuration
```
KAFKA_TOPIC=audio2kafka
KAFKA_BROKER=localhost:9092
```

### Start the Zookeeper server
```
bin/zookeeper-server-start.sh config/zookeeper.properties
```

### Start the Kafka server
```
bin/kafka-server-start.sh config/server.properties
```

### Start the producer
Open the project in a new terminal and run the following commans to start the producer. <br>
```
cd audio2kafka
python3 producer.py
```
This creates a new topic `raw_audio` and the producer will start sending audio files to the Kafka server. Press `Ctrl+C` to stop the producer.

### Start the consumer
```
python3 consumer.py
```
### Start the consumer with audio processing
Currently, audioProcessor/pitchShift.py is used to process the audio files to change the pitch. <br>
```
cd ../audioProcessor
python3 pitchShift.py
```
This creates a new topic `librosa_audio` and sends the processed audio files to this topic. <br>

### Start the consumer to listen to the processed audio
```
cd ../audio2kafka
python3 consumer.py
```
This will listen to the `librosa_audio` topic and save the processed audio files in the `audio2kafka/processed_audio` directory as a .wav file. <br>