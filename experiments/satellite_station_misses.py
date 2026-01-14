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

def get_data_pts(data, pts):
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
    # Get imerg misses
    imerg_miss = get_error_times(get_false_negatives(start_time, end_time, satellite="imerg",
                                                      days=days, precip_threshold=precip_threshold,
                                                      grid=grid, region=region))
    imerg_miss["imerg_miss"] = True  

    # join chirps and imerg misses
    misses = chirps_miss.merge(imerg_miss, on=["lat", "lon", "time"], how="outer")
    misses["time"] = pd.to_datetime(misses["time"])
    # fill nans in imerg_miss and tahmo_miss with False
    misses["imerg_miss"] = misses["imerg_miss"].fillna(False)
    misses["chirps_miss"] = misses["chirps_miss"].fillna(False)

    # Get the pointwise indices of the misses
    miss_pts = xr.Dataset({"time" : ("point", misses.time), 
                           "lat" : ("point", misses.lat), 
                           "lon": ("point", misses.lon),})

    """Add precipitation average values"""
    for precip_source in ["imerg", "chirps", "tahmo_avg"]:
        data = eval(precip_source)(start_time, end_time, grid=grid, region=region, agg_days=days)
        data = get_data_pts(data, miss_pts)
        data = data.rename(columns={"precip": f"{precip_source}_precip"})
        misses = misses.merge(data, on=["time", "lat", "lon"], how="left")

    """Add temperature values"""
    temp = era5(start_time, end_time, variable="tmp2m", grid=grid, region=region, agg_days=days)
    temp = get_data_pts(temp, miss_pts)
    temp = temp.rename(columns={"tmp2m": "era5_tmp2m"})
    misses = misses.merge(temp, on=["time", "lat", "lon"], how="left")
    
    """Get tahmo station counts per cell and join to error_times"""
    # get tahmo counts
    _, tahmo_counts_sparse = get_tahmo_counts(start_time, end_time, grid=grid, region=region)
    # join tahmo_counts to error_times on lat, lon
    misses = misses.merge(tahmo_counts_sparse, on=["lat", "lon"], how="left")
    import pdb; pdb.set_trace()

    """Organize and save results"""
    # order misses by number of stations and time
    misses = misses.sort_values(by=["counts", "time"], ascending=False)
    # convert station_ids to list of strings
    misses["station_ids"] = misses["station_ids"].apply(lambda x: x.tolist())
    # to csv
    dir = "results/satellite_misses"
    file_name = f"{dir}/{region}_{days}d_{precip_threshold}mm_{year}.csv"
    # ssave and make directory if it doesn't exist
    os.makedirs(dir, exist_ok=True)
    misses.to_csv(file_name, index=False)

if __name__ == "__main__":
    start_remote()
    # times to look over
    years = np.arange(2017, 2020)
    # spatial resolution
    grid = 'global0_25'
    # region
    region = "ghana"

    # event definition
    days = 5
    precip_threshold = 38

    days_list = [3, 5, 11, 10]
    precip_threshold_list = [20, 38, 40, 25]

    for event_idx in range(len(days_list)):
        days = days_list[event_idx]
        precip_threshold = precip_threshold_list[event_idx]
        for year in years:
            run_and_save(year, days, precip_threshold, grid, region)

    
