from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
import matplotlib.pyplot as plt
from sheerwater.utils.data_utils import roll_and_agg
import xarray as xr
import numpy as np
import pandas as pd

from sheerwater.tasks.onset_dates import onset_dates
from sheerwater.utils.data_utils import regrid
from sheerwater.spatial_subdivisions import get_spatial_subdivision_level, polygon_subdivision_geodataframe

from sheerwater.utils.space_utils import get_grid

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

def clip_to(ds_src, ds_target):
    # clip ds1 to within ds2
    lat_min, lat_max = float(ds_target.lat.min()), float(ds_target.lat.max())
    lon_min, lon_max = float(ds_target.lon.min()), float(ds_target.lon.max())

    mask = (
        (ds_src.lat >= lat_min) & (ds_src.lat <= lat_max) &
        (ds_src.lon >= lon_min) & (ds_src.lon <= lon_max)
    )

    # rectangular crop
    y_keep, x_keep = mask.any("x"), mask.any("y")
    ds_src_clip = ds_src.isel(y=y_keep.compute(), x=x_keep.compute())
    return ds_src_clip

def regularize(ds, grid):
    ds = ds.set_xindex(("lat", "lon"), xr.indexes.NDPointIndex)
    try:
        _, _, grid_size, _ = get_grid(grid)
    except NotImplementedError:
        grid_size = 0.1

    # get lat/lon table from dates
    loc_table = dates[["lat", "lon"]].to_dataframe().reset_index()
    loc_table = xr.Dataset(coords={"point": np.arange(len(loc_table)), 
    "lat": ("point", loc_table["lat"].values), 
    "lon": ("point", loc_table["lon"].values)})

    ds = ds.sel(
        lat=loc_table["lat"],
        lon=loc_table["lon"],
        method="nearest",
        tolerance=grid_size/2 + 1e-6
    )
    # reshape ds to have lat and lon dimensions
    ds = ds.set_index(point=("lat", "lon")).unstack("point")
    return ds

def get_smap_stats(dates, smap_left, smap_right, grid="global0_25", window_days=14):
    smap_left = clip_to(smap_left, dates)
    smap_right = clip_to(smap_right, dates)

    # regularize smap grid
    smap_left = regularize(smap_left, grid)
    smap_right = regularize(smap_right, grid)
    # assign lat / lon from dates to smap_left and smap_right
    smap_left = smap_left.assign_coords(lat=dates.lat, lon=dates.lon)
    smap_right = smap_right.assign_coords(lat=dates.lat, lon=dates.lon)

    # generate preceding and following masks
    onset_time = dates["time"]
    before = (
        (smap_right.time >= onset_time - np.timedelta64(window_days, "D")) &
        (smap_right.time <= onset_time)
    )
    after = (
        (smap_left.time >= onset_time) &
        (smap_left.time <= onset_time + np.timedelta64(window_days, "D"))
    )
    smap_before = smap_right.where(before)
    smap_after = smap_left.where(after)
    # compute mean, min, max of smap_before and after across time - save as dataset
    smap_before_stats = xr.Dataset(
        {
            "smap_mean": smap_before.soil_moisture.mean("time", skipna=True),
            "smap_min": smap_before.soil_moisture.min("time", skipna=True),
            "smap_max": smap_before.soil_moisture.max("time", skipna=True),
        }
    )
    smap_after_stats = xr.Dataset(
        {
            "smap_mean": smap_after.soil_moisture.mean("time", skipna=True),
            "smap_min": smap_after.soil_moisture.min("time", skipna=True),
            "smap_max": smap_after.soil_moisture.max("time", skipna=True),
        }
    )

    return smap_before_stats, smap_after_stats


if __name__ == "__main__":
    start_remote(remote_name="mohini_soil_slope")

    start_time = "2015-01-01"
    end_time = "2025-12-31"
    grid = "global0_25"

    # get smap data
    agg_days = 5
    smap_ds = get_data("smap_l3")(start_time="2015-01-01", end_time="2025-12-31", grid="source", agg_days=1)
    smap_left = roll_and_agg(smap_ds, agg_days, agg_col="time", agg_fn="mean", agg_thresh=1, align="left")
    smap_right = roll_and_agg(smap_ds, agg_days, agg_col="time", agg_fn="mean", agg_thresh=1, align="right")


    # parameters
    region = "india"
    definition = "icpac_onset"
    time_grouping = "year"

    # onset dates
    dates = onset_dates(start_time, end_time, "imerg_final",
            grid, region, definition, "year")

    smap_before_stats, smap_after_stats = get_smap_stats(dates, smap_left, smap_right)
    
    import pdb; pdb.set_trace()
    grp = "Y"
    selected_groups = [g for g in dates.group.values if grp in str(g)]
    max_before = smap_before_stats.smap_max.sel(group=selected_groups).mean("group")
    min_after = smap_after_stats.smap_min.sel(group=selected_groups).mean("group")
    fig, axs = plt.subplots(1, 3)


    cmap = "managua"
    max_before.plot(ax=axs[0], x="lon", y="lat", cmap=cmap, add_colorbar=False, vmin=0, vmax=0.5)
    min_after.plot(ax=axs[1], x="lon", y="lat", cmap=cmap, add_colorbar=True, vmin=0, vmax=0.5)

    delta = min_after - max_before
    delta.plot(ax=axs[2], x="lon", y="lat", add_colorbar=True, cmap="BrBG",
    norm=TwoSlopeNorm(vmin=-0.1, vcenter=0, vmax=0.1))
    plt.show()
    import pdb; pdb.set_trace()



