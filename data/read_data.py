import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

def read_fdcf_data():
    # TODO: seeing NAN data in fire temperature, area, and power arrays
    file = "OR_ABI-L2-FDCF-M6_G19_s20250010000205_e20250010009513_c20250010010497.nc"
    ds = xr.open_dataset(file)

    print(ds)
    print(ds.data_vars)
    fire_mask = ds['Mask'].values

    print("Fire Mask Shape:", fire_mask.shape)
    print(fire_mask)

    fire_temp = np.where(fire_mask, ds['Temp'].values, np.nan)
    fire_area = np.where(fire_mask, ds['Area'].values, np.nan)
    fire_power = np.where(fire_mask, ds['Power'].values, np.nan)

    print("Fire Temperature Data:")
    print(fire_temp)
    print("Fire Area Data:")
    print(fire_area)
    print("Fire Power Data:")
    print(fire_power)


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
    # plot_cmi_data()
    read_fdcf_data()