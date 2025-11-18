"""mrms data product."""
import xarray as xr
from functools import partial
from sheerwater_benchmarking.utils import regrid, dask_remote, cacheable, roll_and_agg, apply_mask, clip_region
from dateutil import parser
from sheerwater_benchmarking.tasks import spw_rainy_onset, spw_precip_preprocess


@dask_remote
@cacheable(data_type='array',
           timeseries=True,
           cache_args=['grid'],
           chunking={'lat': 300, 'lon': 300, 'time': 365})
def mrms_gridded(start_time, end_time, grid='global0_25'):
    """mrms regridded by year."""
    # Open the datastore
    ds = xr.open_zarr('s3://bkr/mrms/multisensor.zarr', storage_options={'anon': True, 'endpoint_url':'https://data.source.coop'})

    # Rename to lat/lon
    ds = ds.rename({'latitude': 'lat', 'longitude': 'lon', 'MultiSensor_QPE_01H_Pass2': 'precip'})

    # sort by time?
    ds = ds.sortby('time')

    # Agg in the time domain
    ds = ds.resample(time='1D').sum()

    # regrid
    ds = regrid(ds, grid, base='base180', method='conservative')

    return ds


@dask_remote
@cacheable(data_type='array',
           timeseries=['time'],
           cache_args=['grid', 'agg_days'],
           chunking={'lat': 300, 'lon': 300, 'time': 365})
def mrms_rolled(start_time, end_time, agg_days, grid):
    """mrms rolled and aggregated."""

    ds = mrms_gridded(start_time, end_time, grid)

    ds = roll_and_agg(ds, agg=agg_days, agg_col="time", agg_fn='mean')
    return ds


@dask_remote
@cacheable(data_type='array',
           timeseries=['time'],
           cache_args=['variable', 'agg_days', 'grid', 'mask', 'region'],
           cache=False)
def mrms(start_time, end_time, variable, agg_days, grid='global0_25', mask='lsm', region='global'):
    """Final access function for mrms."""
    if variable not in ['precip', 'rainy_onset', 'rainy_onset_no_drought']:
        raise NotImplementedError("Only precip and derived variables provided by mrms.")

    if variable == 'rainy_onset' or variable == 'rainy_onset_no_drought':
        drought_condition = variable == 'rainy_onset_no_drought'
        fn = partial(mrms_rolled, start_time, end_time, grid=grid)
        roll_days = [8, 11] if not drought_condition else [8, 11, 11]
        shift_days = [0, 0] if not drought_condition else [0, 0, 11]
        data = spw_precip_preprocess(fn, agg_days=roll_days, shift_days=shift_days,
                                     mask=mask, region=region, grid=grid)
        ds = spw_rainy_onset(data,
                             onset_group=['ea_rainy_season', 'year'], aggregate_group=None,
                             time_dim='time', prob_type='deterministic',
                             drought_condition=drought_condition,
                             mask=mask, region=region, grid=grid)
        # Rainy onset is sparse, so we need to set the sparse attribute
        ds = ds.assign_attrs(sparse=True)
    else:
        ds = mrms_rolled(start_time, end_time, agg_days, grid)
        ds = apply_mask(ds, mask, grid=grid)
        ds = clip_region(ds, region=region)

    return ds
