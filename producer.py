import json
import time
from kafka import KafkaProducer
import random
from stream_api_data import stream_data


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
            "max_temp_k": random.uniform(200, 500),
            "mean_temp_k": random.uniform(320, 420),
        }


def main():
    """
    Main function to produce wildfire events to Kafka.
    localhost:9092 -> to be used when Kafka is running locally (external)
    kafka:29092 -> to be used when Kafka is running in Docker
    """
    producer = KafkaProducer(
        # bootstrap_servers="kafka:29092",
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    topic = "wildfire-events"

    # Use mock for demo/experimentation purposes
    for event in get_wildfire_events():
        print("Sending event:", event)
        producer.send(topic, value=event)
        producer.flush()
        time.sleep(1)

if __name__ == "__main__":
    main()
