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

### Create the topic
```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic audio2kafka --partitions 1 --replication-factor 1
```
### Delete the topic
```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic audio2kafka
```
