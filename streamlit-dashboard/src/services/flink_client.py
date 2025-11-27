import pandas as pd
import numpy as np
import json
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

# --- ORIGINAL GIT FUNCTION (For Charts & Metrics) ---
# This ensures your main dashboard looks exactly like the Git version
def get_flink_data() -> pd.DataFrame:
    # Synthetic data generation (from original repo)
    rng = np.random.default_rng(42)
    timestamps = pd.date_range(start="2024-01-01 00:00", end="2024-06-01 00:00", periods=300).strftime("%Y-%m-%d %H:%M")
    temperature = rng.normal(loc=300, scale=50, size=300).round(2)
    pixel_counts = rng.normal(loc=130, scale=50, size=300).round().astype(int)
    data = {
        "timestamp": timestamps.tolist(),
        "mean_temp_k": temperature.tolist(),
        "total_pixels": pixel_counts.tolist(),
    }
    return pd.DataFrame(data)

# --- NEW FUNCTION (For Dynamic Table) ---
# This fetches the REAL critical fires (> 2000 K) from Flink
def get_kafka_data() -> pd.DataFrame:
    topic_name = "processed-wildfire-events"
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000
        )
        messages = []
        for _ in range(500):
            try:
                msg = next(consumer)
                event = msg.value
                # Add timestamp if missing
                if 'timestamp' not in event:
                    event['timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                messages.append(event)
            except StopIteration:
                break
        consumer.close()
        return pd.DataFrame(messages) if messages else pd.DataFrame()
    except Exception as e:
        print(f"Kafka Error: {e}")
        return pd.DataFrame()