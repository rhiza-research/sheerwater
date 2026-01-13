from sheerwater.data import chirps, imerg, tahmo_avg
from sheerwater.utils import start_remote
import numpy as np
from sheerwater.metrics import metric
from sheerwater.reanalysis.era5 import era5
from sheerwater.utils.space_utils import clip_region
from sheerwater.utils import get_grid, snap_point_to_grid
from sheerwater.data.tahmo import tahmo_deployment
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import os

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
    grid_counts = clip_region(grid_counts, region=region)

    return grid_counts, sparse_counts

def get_false_negatives(start_time, end_time, days=1, satellite="imerg", precip_threshold=1, grid='global0_25', region="africa"):
    # calculate the average daily precip required to exceed the threshold
    average_precip_threshold = precip_threshold / days
    # call a metric
    fnmetric = metric(start_time, end_time, variable="precip", agg_days=days, grid=grid,
                      forecast=satellite, truth="tahmo_avg", metric_name=f"falsenegative-{average_precip_threshold:.2f}",
                      spatial=True, time_grouping="daily") # don't aggregate by time, get a daily result
    fnmetric = clip_region(fnmetric, region=region)
    return fnmetric

def get_error_times(false_negatives):
    # get a list of time, lat, lon coordinates where the false negatives are
    pts = (
        false_negatives.falsenegative
        .where(false_negatives.falsenegative == 1)
        .stack(point=("time", "lat", "lon"))
        .dropna("point")
        .to_dataframe())
    pts = pts[["time", "lat", "lon"]].reset_index(drop=True)
    return pts

def get_precip_pts(start_time, end_time, source, pts, days=1, grid='global0_25', region='ghana'):
    if source == "imerg":
        data = imerg(start_time, end_time, grid=grid, region=region, agg_days=days)
    elif source == "chirps":
        data = chirps(start_time, end_time, grid=grid, region=region, agg_days=days)
    elif source == "tahmo":
        data = tahmo_avg(start_time, end_time, grid=grid, region=region, agg_days=days)
    else:
        raise ValueError(f"Source {source} not supported")
    data = data.sel(time=pts.time, lat=pts.lat, lon=pts.lon)
    data = data.to_dataframe().reset_index().drop(columns="point")
    # rename precip to source
    data = data.rename(columns={"precip": f"{source}_precip"})
    return data

def get_data_pts(data_fn, start_time, end_time, pts, days=1, grid='global0_25', region='ghana'):
    data = data_fn(start_time, end_time, grid=grid, region=region, agg_days=days)
    data = data.sel(time=pts.time, lat=pts.lat, lon=pts.lon)
    data = data.to_dataframe().reset_index().drop(columns="point")
    return data


def run_and_save(year, days, precip_threshold, grid='global0_25', region='ghana'):
    start_time = f"{year}-01-01"
    end_time = f"{year}-12-31"

    """Get chirps & imerg false negatives times and locations"""
    # Get chirps misses - lat, lon, time dataframe
    chirps_miss = get_error_times(get_false_negatives(start_time, end_time, satellite="chirps",
                                                      days=days, precip_threshold=precip_threshold,
                                                      grid=grid, region=region))
    chirps_miss["chirps_miss"] = True

    # Get false negatives in imerg data (ie imerg missed precipitation event that stations detected)
    satellite = "imerg"
    fn_imerg = get_false_negatives(start_time, end_time, days=days, satellite=satellite, precip_threshold=precip_threshold, grid=grid, region=region)
    # get error times (lat, lon, time) where imerg missed precipitation event that stations detected
    error_times_imerg = get_error_times(fn_imerg)
    error_times_imerg["imerg_miss"] = True

    # join imerg and tahmo error times
    error_times = error_times_chirps.merge(error_times_imerg, on=["lat", "lon", "time"], how="outer")
    # fill nans in imerg_miss and tahmo_miss with False
    error_times["imerg_miss"] = error_times["imerg_miss"].fillna(False)
    error_times["chirps_miss"] = error_times["chirps_miss"].fillna(False)
    # set time to datetime
    error_times["time"] = pd.to_datetime(error_times["time"])

    # Get the pointwise indices of the events, for indexing into data arrays
    error_pts = xr.Dataset({"time" : ("point", error_times.time), 
    "lat" : ("point", error_times.lat), 
    "lon": ("point", error_times.lon),})

    import pdb; pdb.set_trace()
    imerg_data = get_data_pts(imerg, start_time, end_time, error_pts, days=days, grid=grid, region=region)

    """Get imerg, chirps, and tahmo values and join on times"""
    imerg_data = get_precip_pts(start_time, end_time, "imerg", error_pts, days=days, grid=grid, region=region)
    chirps_data = get_precip_pts(start_time, end_time, "chirps", error_pts, days=days, grid=grid, region=region)
    tahmo_data = get_precip_pts(start_time, end_time, "tahmo", error_pts, days=days, grid=grid, region=region)
    # join imerg, chirps, and tahmo data on times to error_times
    error_times = error_times.merge(imerg_data, on=["time", "lat", "lon"], how="left").merge(chirps_data, on=["time", "lat", "lon"], how="left").merge(tahmo_data, on=["time", "lat", "lon"], how="left")

    """Get era5 temperature values and join on times"""
    #era5_data = get_temperature_pts(start_time, end_time, "era5", error_pts, days=days, grid=grid, region=region)
    # join era5 data on times to error_times
    #error_times = error_times.merge(era5_data, on=["time", "lat", "lon"], how="left")
    
    """Get tahmo station counts per cell and join to error_times"""
    # get tahmo counts
    tahmo_counts_grid, tahmo_counts_sparse = get_tahmo_counts(start_time, end_time, grid=grid, region=region)
    # join tahmo_counts to error_times on lat, lon
    error_times = error_times.merge(tahmo_counts_sparse, on=["lat", "lon"], how="left")
    # order error times by number of stations and time
    error_times = error_times.sort_values(by=["counts", "time"], ascending=False)
    # convert station_ids to list of strings
    error_times["station_ids"] = error_times["station_ids"].apply(lambda x: x.tolist())

    """Save results to csv"""
    # to csv
    dir = "results/satellite_misses"
    file_name = f"{dir}/{region}_{days}d_{precip_threshold}mm_{year}.csv"
    # ssave and make directory if it doesn't exist
    os.makedirs(dir, exist_ok=True)
    error_times.to_csv(file_name, index=False)

if __name__ == "__main__":
    start_remote()
    # times to look over
    years = np.arange(2017, 2020)
    # spatial resolution
    grid = 'global0_25'
    # region
    region = "ghana"

    # event definition
    days = 3
    precip_threshold = 20

    for year in years:
        run_and_save(year, days, precip_threshold, grid, region)

    
