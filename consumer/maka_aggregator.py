import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from prometheus_client import start_http_server, Gauge
import json

# Prometheus metrics


# Kafka Consumer setup
class MakaAggregator:
    def __init__(self):
        self.cpu_gauge = Gauge('cpu_utilization', 'CPU usage of the producer', ['producer_id'])
        self.memory_gauge = Gauge('memory_utilization', 'Memory usage of the producer', ['producer_id'])
        for retry in range(20):
            try:
                self.consumer = KafkaConsumer(
                    "cpu_utilization",
                    "memory_utilization",
                    bootstrap_servers='kafka:9093',
                    auto_offset_reset='latest',
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    key_deserializer=lambda v: v.decode('utf-8')
                )
                print("Connected to Kafka broker")
                break
            except NoBrokersAvailable:
                print("Kafka broker not available. Retrying...")
            time.sleep(1)
        else:
            raise Exception("Failed to connect to a Kafka broker.")

    def process_metrics(self):
        for message in self.consumer:
            metrics_event = message.value
            topic = message.topic

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
    aggregator.process_metrics()

