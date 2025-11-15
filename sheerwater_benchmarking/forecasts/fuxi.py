"""Interface for FuXi forecasts."""

import os
import glob
import shutil
import dask
import xarray as xr
import numpy as np
import pandas as pd
import py7zr

from huggingface_hub import hf_hub_download
from huggingface_hub.utils import EntryNotFoundError

from sheerwater_benchmarking.utils.secrets import huggingface_read_token
from sheerwater_benchmarking.utils import (dask_remote, cacheable,
                                           lon_base_change, forecast,
                                           shift_by_days,
                                           roll_and_agg)


@dask_remote
@cacheable(data_type='array', cache_args=['date'])
def fuxi_single_forecast(date):
    """Download a single forecast from the FuXi dataset."""
    token = huggingface_read_token()

    date = str(date).replace('-', '')
    fname = date + '.7z'
    target_path = f"./{fname.replace('.7z', '')}"

    # Download the file
    try:
        path = hf_hub_download(repo_id="FudanFuXi/FuXi-S2S", filename=fname, repo_type="dataset", token=token)
    except EntryNotFoundError:
        print("Skipping invalid forecast date")
        return None

    # unzip the file
    with py7zr.SevenZipFile(path, mode='r') as zip:
        print(f"Extracting {path} to {target_path}")
        zip.extractall(path=target_path)

    files = glob.glob(f"{target_path}/**/*.nc", recursive=True)

    def preprocess(ds):
        """Preprocess the dataset to add the member dimension."""
        ff = ds.encoding["source"]
        member = ff.split('/')[-2]
        ds = ds.assign_coords(member=member)
        ds = ds.expand_dims(dim='member')
        return ds

    # Transform and drop dataa
    print("Opening dataset")
    ds = xr.open_mfdataset(files, engine='netcdf4', preprocess=preprocess)
    # return ds

    ds = ds['__xarray_dataarray_variable__'].to_dataset(dim='channel')

    variables = [
        'tp',
        't2m',
        'd2m',
        'sst',
        'ttr',
        '10u',
        '10v',
        'msl',
        'tcwv'
    ]

    ds = ds[variables]
    ds = ds.compute()

    # Delete the files
    link = os.path.realpath(path)
    os.remove(path)
    os.remove(link)
    shutil.rmtree(target_path)

    return ds


@dask_remote
@cacheable(data_type='array', cache_args=[], timeseries='time',
           chunking={'lat': 121, 'lon': 240, 'lead_time': 14, 'time': 2, 'member': 51},
           validate_cache_timeseries=False)
def fuxi_raw(start_time, end_time, delayed=False):
    """Combine a range of forecasts with or without dask delayed. Returns daily, unagged fuxi timeseries."""
    dates = pd.date_range(start_time, end_time)

    datasets = []
    for date in dates:
        date = date.date()
        if delayed:
            ds = dask.delayed(fuxi_single_forecast)(date, filepath_only=True)
        else:
            ds = fuxi_single_forecast(date, filepath_only=True)
        datasets.append(ds)

    if delayed:
        datasets = dask.compute(*datasets)

    data = [d for d in datasets if d is not None]
    if len(data) == 0:
        print("No data found.")
        return None

    ds = xr.open_mfdataset(data,
                           engine='zarr',
                           combine="by_coords",
                           parallel=True,
                           chunks={'lat': 121, 'lon': 240, 'lead_time': 14, 'time': 2, 'member': 51})

    ds = ds.rename({'tp': 'precip', 't2m': 'tmp2m'})
    return ds


@dask_remote
@cacheable(data_type='array',
           cache_args=['variable', 'agg_days', 'prob_type'],
           chunking={'lat': 121, 'lon': 240, 'lead_time': 14, 'time': 2, 'member': 51})
def fuxi_rolled(start_time, end_time, variable, agg_days=7, prob_type='probabilistic'):
    """Roll and aggregate the FuXi data."""
    ds = fuxi_raw(start_time, end_time)

    # sort the lat dim and change the lon dim
    ds = lon_base_change(ds)
    ds = ds.sortby(ds.lat)

    # Get the right variable
    ds = ds[[variable]]

    # convert based on a linear conversion factor of the average forecast to the era5 average
    if variable == 'precip':
        ds['precip'] = ds['precip'] * 24

    # Convert from kelvin
    if variable == 'tmp2m':
        ds['tmp2m'] = ds['tmp2m'] - 273.15

    # Convert the lead time into a time delta that is 0 indexed
    ds['lead_time'] = ds['lead_time'] - 1
    ds['lead_time'] = ds['lead_time'] * np.timedelta64(1, 'D')

    # If deterministic average across the members
    if prob_type == 'deterministic':
        ds = ds.mean(dim='member')
        ds = ds.assign_attrs(prob_type="deterministic")
    else:
        ds = ds.assign_attrs(prob_type="ensemble")
    ds = roll_and_agg(ds, agg=agg_days, agg_col="lead_time", agg_fn="mean")

    return ds


@dask_remote
@cacheable(data_type='array',
           timeseries='time',
           cache=False,
           cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'])
@forecast
def fuxi(start_time, end_time, variable, agg_days, prob_type='deterministic',
         grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final FuXi forecast interface."""
    if grid != 'global1_5':
        raise NotImplementedError("Only 1.5 grid implemented for FuXi.")

    # The earliest and latest forecast dates for the set of all leads
    forecast_start = shift_by_days(start_time, -46)
    forecast_end = shift_by_days(end_time, 46)

    ds = fuxi_rolled(forecast_start, forecast_end, variable=variable, prob_type=prob_type, agg_days=agg_days)

    # Reanme to standard naming
    ds = ds.rename({'time': 'init_time', 'lead_time': 'prediction_timedelta'})

    # Assign probability label
    prob_label = prob_type if prob_type == 'deterministic' else 'ensemble'
    ds = ds.assign_attrs(prob_type=prob_label)
    return ds
