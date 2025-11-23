import requests
import pandas as pd
import numpy as np

FLINK_JOB_URL = "http://localhost:8081/jobs"  # Update with your Flink job URL

# Fetch data from Flink job
def get_flink_data() -> pd.DataFrame:
    # response = requests.get(FLINK_JOB_URL)
    # if response.status_code == 200:
    #     data = response.json()
    #     return pd.DataFrame(data['results'])  # Adjust based on actual response structure
    # else:
    #     raise Exception(f"Failed to fetch data from Flink job: {response.status_code}")
    # Placeholder implementation using static, synthetic data
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

# Placeholder for data streaming functionality
# Currently not implemented
def stream_data() -> str:
    return "Streaming data from Flink job is not yet implemented."
