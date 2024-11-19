from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import psutil
import time
import socket
import threading
import asyncio


class MakaMonitor:
    def __init__(self, node_id=socket.gethostname()):
        self.KAFKA_INIT_RETRIES = 20
        self.KAFKA_INIT_DELAY = 1 # in seconds
        self.KAFKA_PRODUCER_RETRIES = 5
        self.KAFKA_PRODUCER_DELAY = 1

        self.node_id = node_id
        self.event_loop = asyncio.new_event_loop()

        # Initialize self.producer (Kafka Producer) by connecting to a Kafka broker
        for retry in range(self.KAFKA_INIT_RETRIES):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers='kafka:9093',
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda v: v.encode('utf-8')
                )
                print("Connected to Kafka broker")
                break
            except NoBrokersAvailable:
                print("Kafka broker not available. Retrying...")
            time.sleep(self.KAFKA_INIT_DELAY)
        else:
            raise Exception("Failed to connect to a Kafka broker.")

        # Start the event loop in a separate thread in the background
        self.thread = threading.Thread(target=self.__start_event_loop, daemon=True)
        self.thread.start()

        # Schedule the metric tasks
        asyncio.run_coroutine_threadsafe(self._run(), self.event_loop)


    def __start_event_loop(self):
        print("Starting metric event loop in separate")
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()


    async def _run(self):
        print("Scheduling metric tasks to the event loop")
        await asyncio.gather(self._send_cpu_metrics(), self._send_mem_metrics())


    async def _send_cpu_metrics(self):
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            self.producer.send(topic='cpu_utilization_test', key=self.node_id, value={'cpu_percent': cpu_usage})
            await asyncio.sleep(self.KAFKA_PRODUCER_DELAY, self.event_loop)


    async def _send_mem_metrics(self):
        while True:
            mem_usage = psutil.virtual_memory()
            self.producer.send(topic='mem_utilization_test', key=self.node_id, value={"mem_percent": mem_usage})
            await asyncio.sleep(self.KAFKA_PRODUCER_DELAY, self.event_loop)


if __name__ == "__main__":
    monitor = MakaMonitor()

    # For testing to prevent current process from exiting.
    while True:
        pass