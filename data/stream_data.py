import xarray as xr
import numpy as np
import s3fs
import datetime as dt
import time


AWS_REGION = "us-east-1"
BUCKET_NAME = "noaa-goes19"


def read_fdcf_data(ds): 
    # The dataset already provides some pre-calculated statistics in its metadata.
    # We can access these directly without recalculating them ourselves. This will be faster when working with real time data.
    # --- Use the pre-calculated statistics --- 
    total_fire_pixels = ds['total_number_of_pixels_with_fires_detected'].values
    min_fire_temp = ds['minimum_fire_temperature'].values
    max_fire_temp = ds['maximum_fire_temperature'].values
    mean_fire_temp = ds['mean_fire_temperature'].values

    data = f"Total Pixels (from metadata): {total_fire_pixels}, Min Temp (from metadata): {min_fire_temp} K, Max Temp (from metadata): {max_fire_temp} K, Mean Temp (from metadata): {mean_fire_temp} K"

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
    # year = 2025
    # doy = 100
    # hour = 12
    year = t.year
    doy = int(t.strftime("%j"))
    hour = t.hour
    return f"{BUCKET_NAME}/{product}/{year}/{doy:03d}/{hour:02d}/"


def open_nc_from_s3(fs: s3fs.S3FileSystem, s3_key: str) -> xr.Dataset:
    url = s3_key if s3_key.startswith("s3://") else f"s3://{s3_key}"
    # simplecache downloads to a temp file and keeps it available for random access
    return xr.open_dataset(
        f"simplecache::{url}",
        engine="h5netcdf",
        storage_options={"s3": {"anon": True}},
    )

def stream_data(data_path):
    """
    Stream data from S3 and process it.
    param data_path: the type of data to stream: FDCF, MCMIPC
    """
    fs = s3fs.S3FileSystem(anon=True, client_kwargs={"region_name": AWS_REGION})
    data_path = "ABI-L2-FDCF"

    lookback_hours = 3
    now = dt.datetime.utcnow()
    start = now - dt.timedelta(hours=lookback_hours)
    end = now

    all_full_path = []

    for timestamp in timestamp_range_utc(start, end):
        s3_prefix = get_s3_prefix(data_path, timestamp)
        for key in fs.ls(s3_prefix):
            if not key.endswith(".nc"):
                continue
            if key not in all_full_path:
                all_full_path.append((key, timestamp))
    
    for path, timestamp in all_full_path:
        try:
            ds = open_nc_from_s3(fs, path)
            data = read_fdcf_data(ds)
            print(f"Processing data at time {timestamp}, {path}: {data}")
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            continue


if __name__ == "__main__":
    file = "OR_ABI-L2-FDCF-M6_G19_s20250010000205_e20250010009513_c20250010010497.nc"
    ds = xr.open_dataset(file) 
    # read_fdcf_data(ds)

    stream_data("ABI-L2-FDCF")