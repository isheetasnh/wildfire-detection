import xarray as xr
import numpy as np
import s3fs
import datetime as dt
import time
from kafka import KafkaProducer
import json
import csv
from tqdm import tqdm

AWS_REGION = "us-east-1"
BUCKET_NAME = "noaa-goes19"

# Initialize the producer to connect to Docker container
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8') 
)

def get_confidence_levels(ds):
    fire_confidence_map = {
        10: 1.0, 11: 1.0, 12: 1.0, 13: 1.0, 14: 1.0,
        15: 0.7,                                           
        30: 0.4, 31: 0.4,                                  
        32: 1.0,                                           
        33: 0.5,                                           
        34: 0.5,                                           
        35: 1.0                                            
    }

    mask_data = ds["Mask"].values
    confidence = np.zeros_like(mask_data, dtype=float)
    for code, conf in fire_confidence_map.items():
        confidence[mask_data == code] = conf
    fire_pixels_confidence = confidence[confidence > 0]
    mean_conf = round(fire_pixels_confidence.mean(), 2)
    max_conf = fire_pixels_confidence.max()

    return mean_conf, max_conf

def read_fdcf_data(ds): 
    # Need the following for training data
    # Temp, Power, Area, FireMask, Latitude, Longitude

    fire_pixel_codes = [
        10, 11, 12, 13, 14, 15,  # Standard fire pixels
        30, 31, 32, 33, 34, 35   # Temporally filtered fire pixels
    ]
    mask_data = ds['Mask'].values
    boolean_fire_mask = np.isin(mask_data, fire_pixel_codes)
    temp_data = ds['Temp'].values
    area_data = ds['Area'].values
    power_data = ds['Power'].values
    time_bounds = ds['time_bounds'].values

    mean_confidence, max_confidence = get_confidence_levels(ds)

    fire_temp_full_array = np.where(boolean_fire_mask, temp_data, np.nan)
    fire_area_full_array = np.where(boolean_fire_mask, area_data, np.nan)
    fire_power_full_array = np.where(boolean_fire_mask, power_data, np.nan) 

    actual_fire_temps = fire_temp_full_array[~np.isnan(fire_temp_full_array)]
    actual_fire_areas = fire_area_full_array[~np.isnan(fire_area_full_array)]
    actual_fire_powers = fire_power_full_array[~np.isnan(fire_power_full_array)]

    total_fire_pixels = ds['total_number_of_pixels_with_fires_detected'].values
    max_fire_temp = ds['maximum_fire_temperature'].values
    mean_fire_temp = ds['mean_fire_temperature'].values
    mean_power_fire = ds['mean_fire_radiative_power'].values
    mean_fire_area = ds['mean_fire_area'].values


    data = {
        "n_fire_pixels": total_fire_pixels,
        "mean_temp_fire": mean_fire_temp,
        "max_temp_fire": max_fire_temp,
        "mean_power_fire": mean_power_fire,
        "sum_power_fire": np.sum(actual_fire_powers),
        "mean_area_fire": mean_fire_area,
        "sum_area_fire": np.sum(actual_fire_areas),
        "time_coverage_start": str(time_bounds[0]),
        "time_coverage_end": str(time_bounds[1]),
        "mean_confidence": mean_confidence,
        "max_confidence": max_confidence
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

def get_data(data_path, processed_files_set):
    """
    Stream data from S3 and process it.
    
    param data_path: the type of data to stream: FDCF, MCMIPC
    param processed_files_set: A set of s3 keys that have already been processed.
    """
    # Save files 
    start_time = dt.datetime(2025, 1, 1, 0, 0, 0)
    end_time = dt.datetime(2025, 6, 30, 23, 59, 59)
    new_files_to_process = []
    s3_paths = []
    for timestamp in tqdm(timestamp_range_utc(start_time, end_time)):
        s3_prefix = get_s3_prefix(data_path, timestamp)
        try:
            for key in fs.ls(s3_prefix):
                if not key.endswith(".nc"):
                    continue
                
                if key not in processed_files_set:
                    new_files_to_process.append((key, timestamp))
                    s3_paths.append(key)
        except FileNotFoundError:
            print(f"Warning: S3 prefix not found, skipping: {s3_prefix}")
            continue
    if not new_files_to_process:
        print("No new files found.")
    with open("training_s3_files.json", "w") as f:
        json.dump(s3_paths, f)

    # print(new_files_to_process)
    
    # Now, process only the new files
    fs = s3fs.S3FileSystem(anon=True, client_kwargs={"region_name": AWS_REGION})
    with open("training_s3_files.json", "r") as f:
        new_files_to_process = json.load(f)

    to_write = []
    for path in tqdm(new_files_to_process[:1000]):
        try:
            ds = open_nc_from_s3(fs, path)
            data = read_fdcf_data(ds)
            to_write.append(data)
            
            # New line:
            # print(f"Sending data to Kafka: {data}")
            # Add to our set of processed files *after* successful send
            processed_files_set.add(path)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue
    
    # Return the updated set to the main loop
    
    return to_write



if __name__ == "__main__":    
    # By creating the set *inside* the loop, we "forget" all
    # processed files and re-send them every time.
    processed_files = set() 
    
    data = get_data("ABI-L2-FDCF", processed_files)
    csv_path = "training_data.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)