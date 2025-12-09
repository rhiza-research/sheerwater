"""Fetches ERA5 data from the Google ARCO Store.

NOTE: ERA5 land implementation is in progress.
"""
import numpy as np
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.data import data
from sheerwater.utils import (
    dask_remote,
    get_grid,
    get_grid_ds,
    get_variable,
    lon_base_change,
    regrid,
    roll_and_agg,
)
from sheerwater.utils.secrets import earth_data_hub_token


@dask_remote
@timeseries()
@cache(cache=False,
       cache_args=['variable'])
def era5_land_raw(start_time, end_time, variable):  # noqa ARG001
    """ERA5 function that returns data from earth data hub."""
    token = earth_data_hub_token()
    ds = xr.open_dataset(
        f"https://edh:{token}@data.earthdatahub.destine.eu/era5/reanalysis-era5-land-no-antartica-v0.zarr",
        chunks={},
        # chunks={'time': 365, 'latitude': 300, 'longitude': 300},
        engine="zarr",
    )

    # Select the right variable
    if variable in ['tmax2m', 'tmin2m']:
        var = 'tmp2m'  # Compute min and max daily temperatures from 2m temperature
    var = get_variable(variable, 'era5_land')
    ds = ds[var].to_dataset()

    # Convert local dataset naming and units
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'valid_time': 'time'})

    # Raw latitudes are in descending order
    ds = ds.sortby('lat')
    ds = ds.rename_vars(name_dict={var: variable})

    return ds


@dask_remote
@cache(cache_args=['year', 'variable'],
       backend_kwargs={
           'chunking': {"lat": 300, "lon": 300, "time": 365}
})
def era5_land_daily_year(year, variable):
    """Aggregates the hourly ERA5 data into daily data.

    Args:
        year: The year to fetch data for.
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
            - global0_25: 0.25 degree global grid
    """
    # Read and combine all the data into an array
    start_time = str(year) + '-01-01'
    end_time = str(year) + '-12-31'
    ds = era5_land_raw(start_time, end_time, variable)

    # Convert to base180 longitude
    ds = lon_base_change(ds, to_base="base180")

    K_const = 273.15
    if variable == 'tmp2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').mean(dim='time')
    elif variable == 'tmax2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').max(dim='time')
    elif variable == 'tmin2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').min(dim='time')
    elif variable == 'precip':
        ds[variable] = ds[variable] * 1000.0
        ds.attrs.update(units='mm')
        ds = ds.resample(time='D').sum(dim='time')
        # Can't have precip less than zero (there are some very small negative values)
        ds = np.maximum(ds, 0)
    elif variable == 'ssrd':
        ds = ds.resample(time='D').sum(dim='time')
        ds = np.maximum(ds, 0)
    else:
        raise ValueError(f"Variable {variable} not implemented.")

    ds = ds.chunk({"lat": 300, "lon": 300, "time": 365})
    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable'],
       backend_kwargs={
           'chunking': {"lat": 300, "lon": 300, "time": 365},
})
def era5_land_daily(start_time, end_time, variable):
    """Aggregates the hourly ERA5 data into daily data for a date range.

    Args:
        start_time: Start date for the data range.
        end_time: End date for the data range.
        variable: Variable to fetch.
    """
    years = range(parser.parse(start_time).year, parser.parse(end_time).year + 1)

    datasets = []
    for year in years:
        ds = era5_land_daily_year(year, variable, filepath_only=True)
        datasets.append(ds)

    ds = xr.open_mfdataset(datasets,
                           engine='zarr',
                           parallel=True,
                           chunks={'lat': 300, 'lon': 300, 'time': 365})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'grid'],
       cache_disable_if={'grid': 'global0_1'},
       backend_kwargs={
           'chunking': {"lat": 300, "lon": 300, "time": 365},
})
def era5_land_daily_regrid(start_time, end_time, variable, grid="global0_1"):
    """ERA5 daily reanalysis with regridding."""
    ds = era5_land_daily(start_time, end_time, variable)
    _, _, size, _ = get_grid(grid)
    grid_ds = get_grid_ds(grid)

    ds = ds.reindex_like(grid_ds, method='nearest', tolerance=0.005)

    if grid == 'global0_1':
        return ds

    if size < 0.1:
        raise NotImplementedError("Unable to regrid ERA5 Land smaller than 0.1x0.1")
    else:
        # Regrid onto appropriate grid
        ds = regrid(ds, grid, base='base180', method='conservative')
    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'agg_days', 'grid'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={
           'chunking': {"lat": 300, "lon": 300, "time": 365},
})
def era5_land_rolled(start_time, end_time, variable, agg_days=7, grid="global0_1"):
    """Aggregates the hourly ERA5 data into daily data and rolls.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        agg_days (int): The aggregation period, in days.
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
            - global0_25: 0.25 degree global grid
    """
    # Read and combine all the data into an array
    ds = era5_land_daily_regrid(start_time, end_time, variable, grid=grid)
    if agg_days == 1:
        return ds

    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn="mean")
    return ds


@dask_remote
@data
@timeseries()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def era5_land(start_time, end_time, variable, agg_days, grid='global0_1', mask='lsm', region='global'): # noqa: ARG001
    """Standard format task data for ERA5 Reanalysis.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        agg_days (int): The aggregation period, in days. Ignored if variable is 'rainy_onset'.
        grid (str): The grid resolution to fetch the data at.
        mask (str): The mask to apply to the data.
        region (str): The region to clip the data to.
    """
    _, _, size, _ = get_grid(grid)

    if size < 0.1 or (size == 0.1 and grid != 'global0_1'):
        raise NotImplementedError("Unable to regrid ERA5 Land smaller than 0.1x0.1")

    # Get daily data
    ds = era5_land_rolled(start_time, end_time, variable, agg_days=agg_days, grid=grid)
    return ds


@dask_remote
@timeseries()
@cache(cache=False,
       cache_args=['variable', 'grid'])
def era5_raw(start_time, end_time, variable, grid="global0_25"):  # noqa ARG001
    """ERA5 function that returns data from Google ARCO."""
    if grid != 'global0_25':
        raise NotImplementedError("Only ERA5 native 0.25 degree grid is implemented.")

    # Pull the google dataset
    ds = xr.open_zarr('gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3',
                      chunks={'time': 50, 'latitude': 721, 'longitude': 1440})

    # Select the right variable
    if variable in ['tmax2m', 'tmin2m']:
        var = 'tmp2m'  # Compute min and max daily temperatures from 2m temperature
    var = get_variable(variable, 'era5')
    ds = ds[var].to_dataset()

    # Convert local dataset naming and units
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})

    # Raw latitudes are in descending order
    ds = ds.sortby('lat')
    ds = ds.rename_vars(name_dict={var: variable})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 721, "lon": 1440, "time": 30}
})
def era5_daily(start_time, end_time, variable, grid="global1_5"):
    """Aggregates the hourly ERA5 data into daily data.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
            - global0_25: 0.25 degree global grid
    """
    if grid != 'global0_25':
        raise ValueError("Only ERA5 native 0.25 degree grid is implemented.")

    # Read and combine all the data into an array
    ds = era5_raw(start_time, end_time, variable, grid='global0_25')

    # Convert to base180 longitude
    ds = lon_base_change(ds, to_base="base180")

    K_const = 273.15
    if variable == 'tmp2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').mean(dim='time')
    elif variable == 'tmax2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').max(dim='time')
    elif variable == 'tmin2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(time='D').min(dim='time')
    elif variable == 'precip':
        ds[variable] = ds[variable] * 1000.0
        ds.attrs.update(units='mm')
        ds = ds.resample(time='D').sum(dim='time')
        # Can't have precip less than zero (there are some very small negative values)
        ds = np.maximum(ds, 0)
    elif variable == 'ssrd':
        ds = ds.resample(time='D').sum(dim='time')
        ds = np.maximum(ds, 0)
    else:
        raise ValueError(f"Variable {variable} not implemented.")
    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'grid'],
       cache_disable_if={'grid': 'global0_25'},
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 1000},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'time': 30}
               }
           }
})
def era5_daily_regrid(start_time, end_time, variable, grid="global0_25"):
    """ERA5 daily reanalysis with regridding."""
    ds = era5_daily(start_time, end_time, variable, grid='global0_25')
    ds = ds.sortby('lat')  # TODO: remove if we fix the era5 daily caches
    if grid == 'global0_25':
        return ds

    # Regrid onto appropriate grid
    # Need all lats / lons in a single chunk to be reasonable
    chunks = {'lat': 721, 'lon': 1440, 'time': 30}
    ds = ds.chunk(chunks)
    # Need all lats / lons in a single chunk for the output to be reasonable
    ds = regrid(ds, grid, base='base180', method='conservative', output_chunks={"lat": 121, "lon": 240})
    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'agg_days', 'grid'],
       cache_disable_if={'agg_days': 1},
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 1000},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'time': 30}
               }
           }
})
def era5_rolled(start_time, end_time, variable, agg_days=7, grid="global1_5"):
    """Aggregates the hourly ERA5 data into daily data and rolls.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        agg_days (int): The aggregation period, in days.
        grid (str): The grid resolution to fetch the data at. One of:
            - global1_5: 1.5 degree global grid
            - global0_25: 0.25 degree global grid
    """
    # Read and combine all the data into an array
    ds = era5_daily_regrid(start_time, end_time, variable, grid=grid)
    if agg_days == 1:
        return ds
    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn="mean")
    return ds


@dask_remote
@data
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'])
def era5(start_time=None, end_time=None, variable='precip', agg_days=1,
         grid='global0_25', mask='lsm', region='global'): # noqa: ARG001
    """Standard format task data for ERA5 Reanalysis.

    Args:
        start_time (str): The start date to fetch data for.
        end_time (str): The end date to fetch.
        variable (str): The weather variable to fetch.
        agg_days (int): The aggregation period, in days. Ignored if variable is 'rainy_onset'.
        grid (str): The grid resolution to fetch the data at.
        mask (str): The mask to apply to the data.
        region (str): The region to clip the data to.
    """
    _, _, size, _ = get_grid(grid)
    if size < 0.25:
        raise NotImplementedError("Unable to regrid ERA5 smaller than 0.25x0.25")
    ds = era5_rolled(start_time, end_time, variable, agg_days=agg_days, grid=grid)
    return ds
