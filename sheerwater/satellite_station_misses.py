from sheerwater.data import chirps, imerg, tahmo_avg
from sheerwater.utils import start_remote
import numpy as np
from sheerwater.metrics import metric
from sheerwater.reanalysis.era5 import era5
from sheerwater.spatial_subdivisions import clip_region
from sheerwater.utils import get_grid, snap_point_to_grid
from sheerwater.data.tahmo import tahmo_deployment
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import os
from sheerwater.utils import dask_remote
from nuthatch import cache

def get_tahmo_counts(start_time, end_time, grid='global0_25', region="africa"):
    # Round the coordinates to the nearest grid
    lats, lons, grid_size, offset = get_grid(grid)

    # create emtpy grid initialized with zero station count
    grid_counts = xr.Dataset(coords={'lat': lats, 'lon': lons}, 
                             data_vars={"counts": (['lat', 'lon'], np.zeros((len(lats), len(lons)), dtype=int))})

    stations = tahmo_deployment(start_time, end_time).compute()
    stat = stations.rename(columns={'location_latitude': 'lat', 'location_longitude': 'lon', 'code': 'station_id'})
    stat['lat'] = stat['lat'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    stat['lon'] = stat['lon'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))

    stat = stat[['station_id', 'lat', 'lon']]
    # count the number of stations in each grid cell & make new column with list of station ids 
    sparse_counts = stat.groupby(['lat', 'lon']).agg(station_ids=('station_id', 'unique'),
                                                     counts=('station_id', 'size'))
    # set the counts in the xarray
    grid_counts["counts"] = sparse_counts.counts.to_xarray().reindex_like(grid_counts)
    # clip to the region
    grid_counts = clip_region(grid_counts, region=region, grid=grid)

    return grid_counts, sparse_counts

def get_metric(start_time, end_time, precip_threshold, days, satellite="imerg", truth="tahmo_avg", which_metric="false_negative", grid='global0_25', region='ghana'):
    # calculate the average daily precip required to exceed the threshold
    average_precip_threshold = precip_threshold / days
    # call a metric
    if which_metric == "false_negative":
        metric_name = f"falsenegative-{average_precip_threshold:.2f}"
        rename_dict = {"falsenegative": "metric"}
    elif which_metric == "true_positive":
        metric_name = f"truepositive-{average_precip_threshold:.2f}"
        rename_dict = {"truepositive" : "metric"}
    else:
        raise ValueError(f"Invalid metric: {metric}")
    ds = metric(start_time, end_time, variable="precip", agg_days=days, grid=grid,
                      forecast=satellite, truth=truth, metric_name=metric_name,
                      spatial=True, time_grouping="daily") # don't aggregate by time, get a daily result
    ds = clip_region(ds, region=region, grid=grid)
    # rename metric column to "metric"
    ds = ds.rename(rename_dict)
    return ds

def get_error_times(metric_ds):
    # get a list of time, lat, lon coordinates where the false negatives are
    pts = (
        metric_ds.metric
        .where(metric_ds.metric == 1)
        .stack(point=("time", "lat", "lon"))
        .dropna("point")
        .to_dataframe())
    pts = pts[["time", "lat", "lon"]].reset_index(drop=True)
    pts["time"] = pd.to_datetime(pts["time"])
    return pts

def get_data_pts(data, pts):
    data = data.sel(time=pts.time, lat=pts.lat, lon=pts.lon)
    data = data.to_dataframe().reset_index().drop(columns="point")
    return data

@dask_remote
@cache(cache_args=['satellite', 'truth', 'which_metric', 'grid', 'region', 'days', 'precip_threshold'],
       backend='sql', backend_kwargs={'hash_table_name': True})
def precip_events_table(start_time, end_time, days, precip_threshold,
                 satellite="imerg", truth="tahmo_avg", which_metric="false_negative",
                 grid='global0_25', region='ghana'):

    ds = get_metric(start_time, end_time, precip_threshold, days, satellite, truth, which_metric, grid, region)
    events = get_error_times(ds)
    # Get the pointwise indices of the misses
    event_locs = xr.Dataset({"time" : ("point", events.time), 
                           "lat" : ("point", events.lat), 
                           "lon": ("point", events.lon),})

    """Add temperature values"""
    temp = era5(start_time, end_time, variable="tmp2m", grid=grid, region=region, agg_days=days)
    temp = get_data_pts(temp, event_locs)
    temp = temp.rename(columns={"tmp2m": "era5_tmp2m"})
    events = events.merge(temp, on=["time", "lat", "lon"], how="left")

    """Add precipitation average values"""
    for precip_source in ["imerg", "chirps", "tahmo_avg"]:
        data = eval(precip_source)(start_time, end_time, grid=grid, region=region, agg_days=days)
        data = get_data_pts(data, event_locs)
        data = data.rename(columns={"precip": f"{precip_source}_precip"})
        events = events.merge(data, on=["time", "lat", "lon"], how="left")
    
    """Get tahmo station counts per cell and join to error_times"""
    # get tahmo counts
    _, tahmo_counts_sparse = get_tahmo_counts(start_time, end_time, grid=grid, region=region)
    # join tahmo_counts to error_times on lat, lon
    events = events.merge(tahmo_counts_sparse, on=["lat", "lon"], how="left")

    """Organize and save results"""
    # order misses by number of stations and time
    events = events.sort_values(by=["counts", "time"], ascending=False)
    # convert station_ids to list of strings
    events["station_ids"] = events["station_ids"].apply(lambda x: x.tolist())
    return events

    
