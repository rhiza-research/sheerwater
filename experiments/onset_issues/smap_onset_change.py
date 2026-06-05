"""Plot maps showing change in smap statistics before and after an onset date."""

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

def regularize(ds, dates, grid):
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
    ds = ds.assign_coords(
        lat=("point", loc_table["lat"].values),
        lon=("point", loc_table["lon"].values),
    )
    ds = ds.set_index(point=("lat", "lon")).unstack("point")
    return ds

def get_smap_stats(dates, smap_left, smap_right, grid="global0_25", window_days=14):
    smap_left = clip_to(smap_left, dates)
    smap_right = clip_to(smap_right, dates)

    # regularize smap grid
    smap_left = regularize(smap_left, dates, grid)
    smap_right = regularize(smap_right, dates, grid)

    # generate preceding and following masks
    onset_time = dates["time"]
    before = (
        (smap_right.time >= onset_time - np.timedelta64(window_days, "D")) &
        (smap_right.time < onset_time)
    )
    after = (
        (smap_left.time > onset_time) &
        (smap_left.time <= onset_time + np.timedelta64(window_days, "D"))
    )
    smap_before = smap_right.where(before)
    smap_after = smap_left.where(after)
    # compute mean, min, max of smap_before and after across time - save as dataset
    smap_before_stats = xr.Dataset(
        {
            "smap_mean": smap_before.soil_moisture.mean("time", skipna=True),
            "smap_min": smap_before.soil_moisture.quantile(0.1, dim="time", skipna=True).drop_vars("quantile"),
            "smap_max": smap_before.soil_moisture.quantile(0.9, dim="time", skipna=True).drop_vars("quantile"),
        }
    )

    smap_after_stats = xr.Dataset(
        {
            "smap_mean": smap_after.soil_moisture.mean("time", skipna=True),
            "smap_min": smap_after.soil_moisture.quantile(0.1, dim="time", skipna=True).drop_vars("quantile"),
            "smap_max": smap_after.soil_moisture.quantile(0.9, dim="time", skipna=True).drop_vars("quantile"),
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
    """For india"""
    region = "india"
    time_grouping = "imd_season"
    grp = "preimd" # "imd" or "preimd"
    onset_definitions = ["icpac_onset", "chc_onset", "moron_and_robertson_onset"]

    # """For western africa"""
    # region = "nimbus_west_africa"
    # time_grouping = "year"
    # grp = "Y"
    # onset_definitions = ["icpac_onset", "chc_onset", "moron_and_robertson_onset"]

    # """For eastern africa"""
    # region = "nimbus_east_africa"
    # time_grouping = "two_seasons"
    # grp = "second"
    # onset_definitions = ["icpac_onset", "chc_onset", "moron_and_robertson_onset"]

    fig, axs = plt.subplots(len(onset_definitions), 3)

    onset_idx = 0
    for definition in onset_definitions:
        print(definition)
        # onset dates
        dates = onset_dates(start_time, end_time, "imerg_final",
                grid, region, definition, time_grouping)
        smap_before_stats, smap_after_stats = get_smap_stats(dates, smap_left, smap_right)
    
        # calculate averages across groups
        selected_groups = [g for g in dates.group.values if grp in str(g)]
        max_before = smap_before_stats.smap_max.sel(group=selected_groups).mean("group")
        min_after = smap_after_stats.smap_min.sel(group=selected_groups).mean("group")
        delta = min_after - max_before

        # plot 
        max_before.plot(ax=axs[onset_idx, 0], x="lon", y="lat", cmap="managua", add_colorbar=True, vmin=0, vmax=0.4, add_labels=False)
        min_after.plot(ax=axs[onset_idx, 1], x="lon", y="lat", cmap="managua", add_colorbar=True, vmin=0, vmax=0.4, add_labels=False)
        delta.plot(ax=axs[onset_idx, 2], x="lon", y="lat", cmap="BrBG", add_colorbar=True, norm=TwoSlopeNorm(vmin=-0.1, vcenter=0, vmax=0.1), add_labels=False)

        onset_idx += 1

    # get region boundaries
    try:
        level = get_spatial_subdivision_level(region)[0]
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf["region_name"] == region]
    except Exception as e:
        print(f"Error getting region boundaries: {e}")
        country_gdf = None

    # remove all axis labels
    for ax in axs.flatten():
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("")
        if country_gdf is not None:
            country_gdf.plot(ax=ax, edgecolor="black", linewidth=0.5, facecolor="none")
    
    axs[0, 0].set_title("max sm before")
    axs[0, 1].set_title("min sm after")
    axs[0, 2].set_title("avg min-max change")

    axs[0, 0].set_ylabel(onset_definitions[0])
    axs[1, 0].set_ylabel(onset_definitions[1])
    axs[2, 0].set_ylabel(onset_definitions[2])

    plt.show()



