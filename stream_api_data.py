import xarray as xr
import numpy as np
import s3fs
import datetime as dt
import time
from kafka import KafkaProducer
import json
import random

AWS_REGION = "us-east-1"
BUCKET_NAME = "noaa-goes19"
MAX_LATITUDE = 70.0
MIN_LATITUDE = 15.0
MAX_LONGITUDE = -60.0
MIN_LONGITUDE = -140.0

def read_fdcf_data(ds): 
    # Use the pre-calculated statistics
    total_fire_pixels = ds['total_number_of_pixels_with_fires_detected'].values
    min_fire_temp = ds['minimum_fire_temperature'].values
    max_fire_temp = ds['maximum_fire_temperature'].values
    mean_fire_temp = ds['mean_fire_temperature'].values
    box_west = {"lat_min": 32.0, "lat_max": 48.0, "lon_min": -124.0, "lon_max": -110.0}
    box_central = {"lat_min": 26.0, "lat_max": 49.0, "lon_min": -110.0, "lon_max": -90.0}
    box_east = {"lat_min": 25.0, "lat_max": 45.0, "lon_min": -90.0, "lon_max": -75.0}
    
    # Randomly select one region
    region = random.choice([box_west, box_central, box_east])
    
    latitude = random.uniform(region["lat_min"], region["lat_max"])
    longitude = random.uniform(region["lon_min"], region["lon_max"])
    data = {
        "s3_timestamp": time.time(),
        "total_pixels": int(total_fire_pixels),
        "min_temp_k": float(min_fire_temp),
        "max_temp_k": float(max_fire_temp),
        "mean_temp_k": float(mean_fire_temp),
        "latitude": latitude,
        "longitude": longitude,
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
    
    lookback_hours = 3
    now = dt.datetime.utcnow()
    
    end_time = now - dt.timedelta(hours=2)
    start_time = end_time - dt.timedelta(hours=lookback_hours)

    new_files_to_process = []

    for timestamp in timestamp_range_utc(start_time, end_time):
        s3_prefix = get_s3_prefix(data_path, timestamp)
        try:
            for key in fs.ls(s3_prefix):
                if not key.endswith(".nc"):
                    continue

                if key not in processed_files_set:
                    new_files_to_process.append((key, timestamp))
        except FileNotFoundError:
            # This can happen if data for a specific hour is missing
            print(f"Warning: S3 prefix not found, skipping: {s3_prefix}")
            continue
    
    if not new_files_to_process:
        print("No new files found.")
    
    for path, timestamp in new_files_to_process:
        try:
            ds = open_nc_from_s3(fs, path)
            data = read_fdcf_data(ds)
            yield data
            
            # Add to our set of processed files *after* successful send
            processed_files_set.add(path)
            
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue
    
    return processed_files_set
