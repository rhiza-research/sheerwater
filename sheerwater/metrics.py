"""Verification metrics for forecasters and reanalyses."""
import xarray as xr
from nuthatch import cache
import numpy as np

from sheerwater.metrics_library import metric_factory
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region
from sheerwater.masks import spatial_mask
from sheerwater.utils import dask_remote, groupby_region, groupby_time


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'forecast', 'truth',
                   'metric_name', 'time_grouping', 'space_grouping', 'spatial', 'grid', 'mask', 'region'],
       backend_kwargs={
           'chunking': {"lat": 121, "lon": 240, "time": 100, 'region': 300, 'prediction_timedelta': -1},
           'chunk_by_arg': {
               'grid': {
                   'global0_25': {"lat": 721, "lon": 1440, "time": 30}
               },
           }
})
def metric(start_time, end_time, variable, agg_days, forecast, truth,
           metric_name, time_grouping=None, space_grouping=None,
           spatial=False, grid="global1_5", mask='lsm', region='global'):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    metric_obj = metric_factory(metric_name, start_time=start_time, end_time=end_time, variable=variable,
                                agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                space_grouping=space_grouping, spatial=spatial, grid=grid, mask=mask, region=region)
    return metric_obj.compute()


@dask_remote
@cache(cache_args=['start_time', 'end_time', 'variable', 'agg_days', 'station_data',
                   'time_grouping', 'space_grouping', 'grid', 'mask', 'region', 'missing_thresh'])
def coverage(start_time=None, end_time=None, variable='precip', agg_days=7, station_data='ghcn_avg',
             time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm',
             region='global', missing_thresh=0.9):  # noqa: ARG001
    """Compute coverage of a dataset."""
    # this function does not work for "type" time groupings, because it is hard to evaluate sufficient coverage
    # across all januaries or all Q1s, for example.
    if time_grouping in ["month_of_year", "quarter_of_year"]:
        time_grouping = None

    # Get the station data over the desired period
    # data will have dimensions time (# of agg_days periods) x space (# grid cells)
    station_data_fn = get_data(station_data)
    data = station_data_fn(start_time, end_time, variable, agg_days=agg_days,
                           grid=grid, mask=None, region=region, missing_thresh=missing_thresh)

    # indicate time/space points that are not null (ie adequate coverage)
    # an agg_day - grid cell will be covered if at least one station covers 90% of days
    data['non_null_count'] = data[variable].notnull()
    data['periods_count'] = xr.ones_like(data[variable])
    # count of agg_days periods covered in a time grouping at each cell.
    data = groupby_time(data, time_grouping=time_grouping, agg_fn='sum')

    # get spatial mask for data
    space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping).compute()
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)

    if region != 'global':
        space_grouping_ds = clip_region(space_grouping_ds, region, grid=grid, clip_coords=True)
        mask_ds = clip_region(mask_ds, region, grid=grid, clip_coords=True)

    # three metrics for each spatial group: 
    # 1. count of grid cells in the group
    # 2. count of grid cells with sufficient temporal coverage in the group
    # 3. average of non-empty period counts across grid cells 
    data['cells_count'] = xr.ones_like(data[variable])
    data['cells_covered'] = data['non_null_count'] > temporal_coverage_threshold(time_grouping, agg_days)

    # cells that are not sufficiently covered should not contribute to average coverage
    data['non_null_count'] = data['non_null_count'] * data['cells_covered']
    data = groupby_region(data, space_grouping_ds, mask_ds, agg_fn='sum')
    data['average_cell_periods'] = data['non_null_count'] / data['cells_covered']
    data['periods_count'] = data['periods_count'] / data['cells_count']

    # drop regions named nan (these are outside the mask)
    data = data.sel(region=data.region != 'nan')
    data = data.drop_vars([variable, "non_null_count"])

    return data

def temporal_coverage_threshold(time_grouping, agg_days):
    if time_grouping is None:
        sufficient_days = 365
    elif time_grouping == "month": 
        sufficient_days = 20
    elif time_grouping == "year":
        sufficient_days = 120
    else:
        raise ValueError(f"Invalid time grouping: {time_grouping}")
    return int(sufficient_days / agg_days)

__all__ = ['metric']
