# wildfire-detection

## Development
Create a python env and activate
```
python3 -m venv .venv
source .venv/bin/activate
```

Install relevant packages
```
pip install requirements.txt
```

Folder structure:
* All data related script and datasets
- read_data.py -> experiments with reading sample FDCF and MCMIPC dataset
- simulate_realtime -> 

## Data Source
The data can be found in AWS S3 bucket: https://noaa-goes19.s3.amazonaws.com/index.html
The dataset relevant for firedetection includes:
- ABI-L2-FDCF   => Fire detection and characterization    
- ABI-L2-FM1    => Fire Mask
- ABI-L2-MCMIPC => multi-channel imagery

The GOES-19 is stationary at -> Longitude: 137.0°W (−137.0°), Altitude: 35,786 km above the equator.
It is observing:
* All of the western United States
* Pacific Ocean
* Alaska, Hawaii
* Central America
* Parts of South America
