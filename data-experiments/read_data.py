import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

def read_fdcf_data(): 
    file = "OR_ABI-L2-FDCF-M6_G19_s20250010000205_e20250010009513_c20250010010497.nc"
    ds = xr.open_dataset(file) 
    # 1. Define all codes that mean "fire" based on your 'flag_meanings' output
    # We include all probabilities and filtered pixels
    fire_pixel_codes = [
        10, 11, 12, 13, 14, 15,  # Standard fire pixels
        30, 31, 32, 33, 34, 35   # Temporally filtered fire pixels
    ]

    # 2. Get the full 2D array of mask codes
    mask_data = ds['Mask'].values

    # 3. Create a TRUE boolean mask:
    # This will be an array of True/False values.
    # True only where a fire pixel code was detected, False everywhere else.
    boolean_fire_mask = np.isin(mask_data, fire_pixel_codes)

    # 4. Get the corresponding data from the variables
    # The 'ds.data_vars' output confirms these are the correct names
    temp_data = ds['Temp'].values
    area_data = ds['Area'].values
    power_data = ds['Power'].values

    # 5. Apply the boolean mask to extract the data.
    # np.where(condition, value_if_true, value_if_false)
    # This creates the 2D arrays, but they will be 99.99% NAN
    fire_temp_full_array = np.where(boolean_fire_mask, temp_data, np.nan)
    fire_area_full_array = np.where(boolean_fire_mask, area_data, np.nan)
    fire_power_full_array = np.where(boolean_fire_mask, power_data, np.nan) 

    # Don't print the whole 2D array.
    # Instead, filter the arrays to get ONLY the actual numbers. We don't want to print the entire map, we only filter out
    # the pixels where fires were detected and only print those values.
    # The `~np.isnan()` part selects only the non-NAN values.

    actual_fire_temps = fire_temp_full_array[~np.isnan(fire_temp_full_array)]
    actual_fire_areas = fire_area_full_array[~np.isnan(fire_area_full_array)]
    actual_fire_powers = fire_power_full_array[~np.isnan(fire_power_full_array)]
 
    print(f"Total fire pixels detected: {len(actual_fire_temps)}")

    print("\nFire Temperature Data (Kelvin):")
    print(actual_fire_temps)

    print("\nFire Area Data (m^2):")
    print(actual_fire_areas)

    print("\nFire Power Data (MW):")
    print(actual_fire_powers)
    # The dataset already provides some pre-calculated statistics in its metadata.
    # We can access these directly without recalculating them ourselves. This will be faster when working with real time data.
    # --- Use the pre-calculated statistics --- 
    print(f"Total Pixels (from metadata): {ds['total_number_of_pixels_with_fires_detected'].values}")
    print(f"Min Temp (from metadata):   {ds['minimum_fire_temperature'].values} K")
    print(f"Max Temp (from metadata):   {ds['maximum_fire_temperature'].values} K")
    print(f"Mean Temp (from metadata):  {ds['mean_fire_temperature'].values} K")


# plot the Calibrated, Mapped, and Interpolated (CMI) data from GOES ABI
# CMI consits of multiple bands, each representing different wavelengths of light
# CMI_07 -> is the fire-sensitive channel (3.9 µm)
def plot_cmi_data():
    file = "OR_ABI-L2-MCMIPC-M6_G19_s20250010001173_e20250010003557_c20250010004071.nc"
    ds = xr.open_dataset(file)

    # print(ds)
    # print(ds.data_vars)

    # CMI_07
    band_data = ds["CMI_C07"]
    print(band_data)

    proj = ccrs.Geostationary(satellite_height=35786023)
    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=proj)
    band_data.plot.imshow(ax=ax, transform=proj, cmap='inferno', add_colorbar=True)
    ax.coastlines()
    plt.title("GOES-19 Band 7 (3.9 µm) – Fire-Sensitive Channel")
    plt.show()


if __name__ == "__main__":
    plot_cmi_data()
    read_fdcf_data()