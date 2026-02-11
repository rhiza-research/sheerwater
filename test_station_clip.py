from sheerwater.interfaces import get_data
from sheerwater.utils import start_remote

from sheerwater.data.tahmo import tahmo, tahmo_raw
from sheerwater.data.ghcn import ghcn
from sheerwater.data.knust import knust_raw

from sheerwater.spatial_subdivisions import clip_region
from sheerwater.spatial_subdivisions import spatial_subdivisions
import numpy as np
import shapely
import xarray as xr

import matplotlib.pyplot as plt


if __name__ == "__main__":
    start_remote()
    # get tahmo data on tahmo grid
    start_time, end_time = "2012-01-01", "2025-03-01"
    tahmo_data = tahmo_raw(start_time, end_time, grid="tahmo")
    knust_data = knust_raw(start_time, end_time, grid="knust")

    region = "ghana"
    knust_clipped = clip_region(knust_data, region=region, grid="knust")
    import pdb; pdb.set_trace(header="knust clipped")
    

    plt.scatter(knust_data["lon"].values, knust_data["lat"].values, s=5, color='red')
    plt.scatter(knust_clipped["lon"].values, knust_clipped["lat"].values, s=5, color='green')

    # print the original stations and number dropped
    print(f"Original stations: {len(knust_data.station_id)}")
    print(f"Kept stations: {len(knust_clipped.station_id)}")

    import pdb; pdb.set_trace()