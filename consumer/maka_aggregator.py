import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from prometheus_client import start_http_server, Gauge
import json

# Kafka Consumer setup
class MakaAggregator:
    def __init__(self):
        self.KAFKA_INIT_RETRIES = 20
        self.KAFKA_INIT_DELAY = 1 # in seconds
        self.KAFKA_PRODUCER_RETRIES = 5
        self.KAFKA_PRODUCER_DELAY = 1
        self.cpu_gauge = Gauge('cpu_utilization', 'CPU usage of the producer', ['producer_id'])
        self.memory_gauge = Gauge('memory_utilization', 'Memory usage of the producer', ['producer_id'])

        for retry in range(self.KAFKA_INIT_RETRIES):
            try:
                self.consumer = KafkaConsumer(
                    "cpu_utilization",
                    "memory_utilization",
                    bootstrap_servers=['kafka-1:9093','kafka-2:9093'],
                    auto_offset_reset='earliest',
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    key_deserializer=lambda v: v.decode('utf-8'),
                    group_id="maka-aggregator-group"
                )
                print("Connected to Kafka broker")
                break
            except NoBrokersAvailable:
                print("Kafka broker not available. Retrying...")
            time.sleep(self.KAFKA_INIT_DELAY)
        else:
            raise Exception("Failed to connect to a Kafka broker.")

    def consume_messages(self):
        print("Consuming messages")
        for message in self.consumer:
            metrics_event = message.value
            topic = message.topic

            print(f"Messages: {message}")

            if topic == "cpu_utilization":
                cpu_usage = metrics_event['cpu_percent']
                self.cpu_gauge.labels(message.key).set(cpu_usage)
            elif topic == "memory_utilization":
                memory_usage = metrics_event['mem_percent']
                self.memory_gauge.labels(message.key).set(memory_usage)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)

    # Process metrics from Kafka
    aggregator = MakaAggregator()
    aggregator.consume_messages()

