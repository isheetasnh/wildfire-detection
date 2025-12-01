import json
import time
from kafka import KafkaProducer
import random
from stream_api_data import stream_data

METRIC_FILE_PATH = "systems_monitor/producer_metrics_log.jsonl"
def init_metric_file(path):
    with open(path, "w") as f:
        pass


metrics = {
    "messages_sent": 0,
    "timestamp": time.time(),
    "throughput_msgs_per_sec": 0.0,
    "last_latency_sec": 0.0
}

def get_wildfire_events():
    """
    Stream data from the NOAA GOES-19 satellite S3 buckets.
    """
    while True:
        processed_files = set() 
        try:
            yield from stream_data("ABI-L2-FDCF", processed_files)
        except Exception as e:
            print(f"An unexpected error occurred in stream_data: {e}")
        
        time.sleep(1)


def get_mock_wildfire_events():
    """
    Generate mock wildfire event data for testing.
    """
    while True:
        yield {
            "total_pixels": random.randint(1, 100),
            "min_temp_k": random.uniform(300, 350),
            "max_temp_k": random.uniform(200, 5000),
            "mean_temp_k": random.uniform(320, 420),
        }

def write_metrics(metric):
    with open(METRIC_FILE_PATH, "a") as f:
        f.write(json.dumps(metric) + "\n")


def main(begin_time):
    """
    Main function to produce wildfire events to Kafka.
    localhost:9092 -> to be used when Kafka is running locally (external)
    kafka:29092 -> to be used when Kafka is running in Docker
    """
    init_metric_file(METRIC_FILE_PATH)
    producer = KafkaProducer(
        # bootstrap_servers="kafka:29092",
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    topic = "wildfire-events"

    # Use mock for demo/experimentation purposes
    for event in get_wildfire_events():
        time.sleep(3)
        print("Sending event:", event)
        start = time.time()
        producer.send(topic, value=event)
        producer.flush()
        end = time.time()

        latency = end - start
        metrics["last_latency_sec"] = latency
        metrics["messages_sent"] += 1

        # time elapsed since the beginning of the script
        elapsed = end - begin_time
        if elapsed > 0:
            metrics["throughput_msgs_per_sec"] = metrics["messages_sent"] / elapsed

        metrics["timestamp"] = time.time()
        write_metrics(metrics)

        time.sleep(1)

if __name__ == "__main__":
    begin_time = time.time()
    main(begin_time)
