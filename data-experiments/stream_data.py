import xarray as xr
import numpy as np
import s3fs
import datetime as dt
import time
from kafka import KafkaProducer
import json

AWS_REGION = "us-east-1"
BUCKET_NAME = "noaa-goes19"

# Initialize the producer to connect to Docker container
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8') 
)

def read_fdcf_data(ds): 
    # Use the pre-calculated statistics
    total_fire_pixels = ds['total_number_of_pixels_with_fires_detected'].values
    min_fire_temp = ds['minimum_fire_temperature'].values
    max_fire_temp = ds['maximum_fire_temperature'].values
    mean_fire_temp = ds['mean_fire_temperature'].values

    data = {
        "total_pixels": int(total_fire_pixels),
        "min_temp_k": float(min_fire_temp),
        "max_temp_k": float(max_fire_temp),
        "mean_temp_k": float(mean_fire_temp)
    }
    return data

def timestamp_range_utc(start: dt.datetime, end: dt.datetime, delta: dt.timedelta = dt.timedelta(hours=1)):
    cur = start.replace(minute=0, second=0, microsecond=0)
    end = end.replace(minute=0, second=0, microsecond=0)
    timestamps = []
    while cur <= end:
        timestamps.append(cur)
        cur += dt.timedelta(hours=1)
    return timestamps

def get_s3_prefix(product: str, t: dt.datetime):
    # NOAA layout: s3://{bucket}/{product}/{YYYY}/{DOY}/{HH}/
    year = t.year
    doy = int(t.strftime("%j"))
    hour = t.hour
    return f"{BUCKET_NAME}/{product}/{year}/{doy:03d}/{hour:02d}/"


def open_nc_from_s3(fs: s3fs.S3FileSystem, s3_key: str) -> xr.Dataset:
    url = s3_key if s3_key.startswith("s3://") else f"s3://{s3_key}"
    return xr.open_dataset(
        f"simplecache::{url}",
        engine="h5netcdf",
        storage_options={"s3": {"anon": True}},
    )

def stream_data(data_path, processed_files_set):
    """
    Stream data from S3 and process it.
    
    param data_path: the type of data to stream: FDCF, MCMIPC
    param processed_files_set: A set of s3 keys that have already been processed.
    """ 
    fs = s3fs.S3FileSystem(anon=True, client_kwargs={"region_name": AWS_REGION})
    # data_path = "ABI-L2-FDCF" # This is passed in, no need to hardcode
    
    lookback_hours = 3
    now = dt.datetime.utcnow()
    
    # --- FIX 1: LATENCY ---
    # Process data up to 1 hour ago.
    # This avoids asking for the current hour's data, which may not exist yet.
    end_time = now - dt.timedelta(hours=2)
    start_time = end_time - dt.timedelta(hours=lookback_hours)

    new_files_to_process = []

    for timestamp in timestamp_range_utc(start_time, end_time):
        s3_prefix = get_s3_prefix(data_path, timestamp)
        try:
            for key in fs.ls(s3_prefix):
                if not key.endswith(".nc"):
                    continue
                
                # --- FIX 2: DUPLICATION ---
                # Only add files we have not processed before.
                if key not in processed_files_set:
                    new_files_to_process.append((key, timestamp))
        except FileNotFoundError:
            # This can happen if data for a specific hour is missing
            print(f"Warning: S3 prefix not found, skipping: {s3_prefix}")
            continue
    
    if not new_files_to_process:
        print("No new files found.")
    
    # Now, process only the new files
    for path, timestamp in new_files_to_process:
        try:
            ds = open_nc_from_s3(fs, path)
            data = read_fdcf_data(ds)
            
            # New line:
            print(f"Sending data to Kafka: {data}")
            producer.send('wildfire-events', value=data)
            
            # Add to our set of processed files *after* successful send
            processed_files_set.add(path)
            
            time.sleep(1) # Small delay to not overwhelm Kafka
        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue
    
    # Return the updated set to the main loop
    return processed_files_set



if __name__ == "__main__":
    
    while True:
        print("\n--- [TESTING MODE] Re-streaming all files in lookback window... ---")
        
        # By creating the set *inside* the loop, we "forget" all
        # processed files and re-send them every time.
        processed_files = set() 
        
        try:
            stream_data("ABI-L2-FDCF", processed_files)
        except Exception as e:
            print(f"An unexpected error occurred in stream_data: {e}")
            
        # Shorter sleep time for more continuous streaming
        print(f"\n--- Test batch complete. Waiting 10 seconds to re-stream... ---")
        time.sleep(10)