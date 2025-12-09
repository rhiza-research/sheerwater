"""Interface for gencast forecasts."""
import gcsfs
import numpy as np
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.forecasts.forecast_decorator import forecast
from sheerwater.utils import dask_remote, lon_base_change, regrid, roll_and_agg, shift_by_days


@dask_remote
@cache(cache_args=['year', 'variable', 'init_hour'],
       backend_kwargs={'chunking': {"lat": 721, "lon": 1440, 'lead_time': 10, 'time': 1, 'member': 5}})
def gencast_daily_year(year, variable, init_hour=0):
    """A daily Gencast forecast."""
    if init_hour != 0:
        raise ValueError("Only 0 init hour supported")

    # Get glob of all gencast forecasts
    fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')

    def get_sub_ds(root):
        """Iterates through the root folder to find all sub zarrs for the requested year."""
        members = fs.ls(root, detail=False)
        members = members[1:]
        zarrs = []
        for mem in members:
            """Open a zarr for each member set."""
            mem_path = mem + '/forecasts_15d/'
            zarr = fs.ls(mem_path, detail=False)
            zarr = 'gs://' + zarr[0]
            ds = xr.open_zarr(zarr, chunks='auto', decode_timedelta=True)

            # Evaluation WIDs <= 7 are done with 0/12hr leads - >7 are 6/18hr leads.
            if ds.attrs['evaluation_wid'] <= 7:
                zarrs.append(zarr)
            else:
                print("Skipping 6/18hr leads.")

        return zarrs

    zarrs = []

    if year == '2020':
        zarrs += get_sub_ds('gs://weathernext/126478713_1_0/zarr/124883614_2020_to_2021')
    elif year == '2021':
        zarrs += get_sub_ds('gs://weathernext/126478713_1_0/zarr/124958964_2021_to_2022')
    elif year == '2022':
        zarrs += get_sub_ds('gs://weathernext/126478713_1_0/zarr/125057031_2022_to_2023')
    elif year == '2023':
        zarrs += get_sub_ds('gs://weathernext/126478713_1_0/zarr/125156073_2023_to_2024')

    ds = xr.open_mfdataset(zarrs,
                           chunks='auto',
                           decode_timedelta=True,
                           engine='zarr',
                           drop_variables=['100m_u_component_of_wind',
                                           '100m_v_component_of_wind',
                                           '10m_u_component_of_wind',
                                           '10m_v_component_of_wind',
                                           'geopotential',
                                           'mean_sea_level_pressure',
                                           'sea_surface_temperature',
                                           'specific_humidity',
                                           'temperature',
                                           'u_component_of_wind',
                                           'v_component_of_wind',
                                           'vertical_velocity'
                                           ])

    # Read the three years for gcloud
    ds = ds.rename({'prediction_timedelta': 'lead_time',
                    '2m_temperature': 'tmp2m',
                    'total_precipitation_12hr': 'precip',
                    'sample': 'member'})
    ds = ds[[variable]]

    # Select only the midnight initialization times
    ds = ds.where(ds.time.dt.hour == init_hour, drop=True)

    # Convert units
    K_const = 273.15
    if variable == 'tmp2m':
        ds[variable] = ds[variable] - K_const
        ds.attrs.update(units='C')
        ds = ds.resample(lead_time='1D').mean(dim='lead_time')
    elif variable == 'precip':
        ds[variable] = ds[variable] * 1000.0
        ds.attrs.update(units='mm')

        # Convert from 12hrly to daily precip, robust to different numbers of 12hrly samples in a day
        ds = ds.resample(lead_time='1D').mean(dim='lead_time') * 2.0

        # Can't have precip less than zero (there are some very small negative values)
        ds = np.maximum(ds, 0)
    else:
        raise ValueError(f"Variable {variable} not implemented.")

    # Shift the lead back 12 hours + init time to be aligned
    ds['lead_time'] = ds['lead_time'] - np.timedelta64(init_hour+12, 'h')

    # Convert lat/lon
    ds = lon_base_change(ds)

    # This was necessary?
    ds = ds.chunk({"lat": 721, "lon": 1440, 'lead_time': 10, 'time': 1, 'member': 5})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "lead_time": 10, "time": 10, 'member': 10},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'lead_time': 10, 'time': 1, 'member': 5}
               },
           }
})
def gencast_daily(start_time, end_time, variable, grid='global0_25'):  # noqa: ARG001
    """A daily gencast forecast."""
    ds1 = gencast_daily_year(year='2020', variable=variable, init_hour=0)
    ds2 = gencast_daily_year(year='2021', variable=variable, init_hour=0)
    ds3 = gencast_daily_year(year='2022', variable=variable, init_hour=0)

    ds = xr.concat([ds1, ds2, ds3], dim='time')

    # This was necessary?
    ds = ds.chunk({'lat': 721, 'lon': 1440, 'lead_time': 10, 'time': 1, 'member': 5})

    # Regrid
    if grid != 'global0_25':
        ds = regrid(ds, grid, base='base180', method='conservative',
                    output_chunks={"lat": 721, "lon": 1440})

    return ds


@dask_remote
@timeseries()
@cache(cache_args=['variable', 'agg_days', 'prob_type', 'grid'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "lead_time": 10, "time": 10, "member": 10},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, 'lead_time': 10, 'time': 1, 'member': 5}
               },
           }
})
def gencast_rolled(start_time, end_time, variable, agg_days, prob_type='deterministic', grid='global0_25'):
    """A rolled and aggregated gencast forecast."""
    ds = gencast_daily(start_time, end_time, variable, grid)

    if prob_type == 'deterministic':
        ds = ds.mean(dim='member')
        ds = ds.assign_attrs(prob_type="deterministic")
    else:
        ds = ds.assign_attrs(prob_type="ensemble")

    ds = roll_and_agg(ds, agg=agg_days, agg_col="lead_time", agg_fn="mean")
    return ds


@dask_remote
@timeseries()
@forecast
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'prob_type', 'grid', 'mask', 'region'])
def gencast(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',
            grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final Gencast interface."""
    if variable != 'precip':
        raise NotImplementedError("Data error present in non-precip variables in Gencast. Skipping.")

    # Get the data with the right days
    forecast_start = shift_by_days(start_time, -15) if start_time is not None else None
    forecast_end = shift_by_days(end_time, 15) if end_time is not None else None

    # Get the data with the right days
    ds = gencast_rolled(start_time=forecast_start, end_time=forecast_end, variable=variable,
                        agg_days=agg_days, prob_type=prob_type, grid=grid)
    if prob_type == 'deterministic':
        ds = ds.assign_attrs(prob_type="deterministic")
    else:
        ds = ds.assign_attrs(prob_type="ensemble")

    # Rename to standard naming
    ds = ds.rename({'time': 'init_time', 'lead_time': 'prediction_timedelta'})
    return ds
