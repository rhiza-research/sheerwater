"""Interface for GFS forecasts."""
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, shift_by_days, get_grid, regrid
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial


@dask_remote
@timeseries(timeseries='init_time')
@spatial()
@cache(cache_args=['variable', 'grid', 'prob_type'],
       backend_kwargs={'chunking': {'lat': 121, 'lon': 240, 'lead_time': 35, 'time': 3, 'member': 30}},
       cache_disable_if={
           'grid': 'global0_25'
       })
def gfs_raw(start_time, end_time, variable='precip', prob_type='deterministic', grid='global1_5', # noqa: ARG001
            mask=None, region='global'):  # noqa: ARG001
    """Access GFS/GEFS raw."""
    # Fetched from earthmover directly into our bucket. Already meaned across members
    ds = xr.open_zarr('gs://sheerwater-datalake/gefs/gefs.zarr/')

    # Select the variable
    if variable != 'precip'  and variable != 'tmp2m':
        raise ValueError("Currently only supports precip and temp")

    ds = ds[[variable]]

    # If it's deterministic take the ensemble mean
    if prob_type != 'deterministic':
        raise ValueError("Currently only supports deterministic forecasts")

    _, _, size, _  = get_grid(grid)

    if size < 0.25:
        raise ValueError("GFS only supports grids of 0.25 or less.")

    if grid != 'global0_25':
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'processors', 'processor_kwargs',
                   'lookback_source', 'densify', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 10, 'lead_time': 35, 'member': 1}})
def gfs(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic', # noqa: ARG001
        event=None, event_kwargs=None,  # noqa: ARG001
        processors=None, processor_kwargs=None,  # noqa: ARG001
        lookback_source=None, densify=False,  # noqa: ARG001
        grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final GFS forecast interface."""
    # The earliest and latest forecast dates for the set of all leads
    forecast_start = shift_by_days(start_time, -35) if start_time is not None else None

    ds = gfs_raw(forecast_start, end_time, variable,
                 prob_type=prob_type, grid=grid, mask=mask,
                 region=region)

    # Reanme to standard naming
    ds = ds.rename({'lead_time': 'prediction_timedelta'})

    # Assign probability label
    ds = ds.assign_attrs(prob_type='deterministic')
    return ds
