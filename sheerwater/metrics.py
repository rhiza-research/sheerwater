"""Verification metrics for forecasters and reanalyses."""
import xarray as xr
from nuthatch import cache
import warnings
import numpy as np

from sheerwater.metrics_library import metric_factory
from sheerwater.interfaces import get_data, get_forecast
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
def station_coverage(start_time=None, end_time=None, variable='precip', agg_days=7, station_data='ghcn_avg',
             time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm',
             region='global', missing_thresh=0.9):  # noqa: ARG001
    """Compute coverage of a dataset.

    Returns a dataset with the following variables:
    - total_cells: count of grid cells in each space_group
    - total_periods: count of agg_days periods per time_group
    - cells_covered: the number of cells within the space_grouping which meet a temporal coverage threshold
    - average_periods_covered: the average number of time periods of coverage of cells that are sufficiently covered.
    """
    # this function does not apply "type" time groupings, because it is hard to evaluate sufficient coverage
    # across all januaries or all Q1s, for example. Instead, it is better to look at coverage over the entire period.
    # This is what the function falls back to if time_grouping is a type.
    if time_grouping in ["month_of_year", "quarter_of_year"]:
        warnings.warn(f"Time grouping {time_grouping} is not supported for coverage calculation.")
        time_grouping = None

    # helper function which defines temporal coverage sufficiency thresholds
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

    # Get the station data over the desired period
    # data will have dimensions time (# of agg_days periods) x space (# grid cells)
    station_data_fn = get_data(station_data)
    data = station_data_fn(start_time, end_time, variable, agg_days=agg_days,
                           grid=grid, mask=None, region=region, missing_thresh=missing_thresh)

    # indicate time/space points that are not null (ie adequate coverage)
    # an agg_day - grid cell will be covered if at least one station covers 90% of days
    data['non_null_count'] = data[variable].notnull()
    data['total_periods'] = xr.ones_like(data[variable])
    # count of agg_days periods covered in a time grouping at each cell.
    data = groupby_time(data, time_grouping=time_grouping, agg_fn='sum')

    # get spatial mask for data
    space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping).compute()
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)

    if region != 'global':
        coords_to_clip = [coord for coord in space_grouping_ds.coords if 'region' in coord]
        space_grouping_ds = clip_region(space_grouping_ds, region, grid=grid, coords_to_clip=coords_to_clip)
        mask_ds = clip_region(mask_ds, region, grid=grid)

    # three metrics for each spatial group:
    # 1. count of grid cells in the group
    # 2. count of grid cells with sufficient temporal coverage in the group
    # 3. average of non-empty period counts across grid cells
    data['total_cells'] = xr.ones_like(data[variable])
    data['cells_covered'] = data['non_null_count'] > temporal_coverage_threshold(time_grouping, agg_days)

    # cells that are not sufficiently covered should not contribute to average coverage
    data['non_null_count'] = data['non_null_count'] * data['cells_covered']
    data = groupby_region(data, space_grouping_ds, mask_ds, agg_fn='sum')
    data['average_periods_covered'] = data['non_null_count'] / data['cells_covered']
    data['total_periods'] = data['total_periods'] / data['total_cells']

    # drop regions named nan (these are outside the mask)
    data = data.sel(region=data.region != 'nan')
    data = data.drop_vars([variable, "non_null_count"])

    # rename the coordinates
    if isinstance(region, str) and region != 'global':
        # rename values of region coordinates from 'global' to the region name
        for coord in [coord for coord in data.coords if 'region' in coord]:
            data[coord] = data[coord].astype(str).str.replace('global', region)

    return data


@dask_remote
#@cache(cache_args=['satellite', 'station', 'station_threshold', 'agg_days', 'grid', 'region'],
#       backend='sql', backend_kwargs={'hash_table_name': True})
def auc(start_time, end_time, satellite, station, station_threshold='climatology_tahmo_avg_2015_2025', agg_days=7, 
        time_grouping=None, space_grouping=None, grid='global1_5', mask='lsm', region='global', spatial=False):
    """Compute the AUC-ROC curve for a satellite and station."""
    satellite_data = get_data(satellite)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)
    station_data = get_data(station)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)
    # get maximum rainfall in satellite data
    nan_mask = satellite_data.precip.isnull() | station_data.precip.isnull()
    max_rainfall = satellite_data.where(~nan_mask).precip.max().values

    if isinstance(station_threshold, str):
        station_threshold = get_forecast(station_threshold)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)
        station_data = station_data - station_threshold.isel(prediction_timedelta=0).rename({'precip': f'{station_threshold}_precip'})
        station_data = station_data.drop_vars('prediction_timedelta')
    # if the threshold is a number, subtract it from the station data
    elif isinstance(station_threshold, (float, int)):
        station_data = station_data - station_threshold

    # threshold descending -> false positive rate increasing, as expected by auc integration
    step = max(0.01, max_rainfall / 300)
    thresholds = np.arange(0, max_rainfall + step, step)[::-1]
    thresholds = xr.DataArray(
        thresholds,
        dims="threshold",
        coords={"threshold": thresholds}
    )

    satellite_event = (satellite_data.precip >= thresholds)
    station_event = (station_data.precip >= 0)

    true_pos = (satellite_event & station_event) & ~nan_mask
    false_pos = (satellite_event & ~station_event) & ~nan_mask
    false_neg = (~satellite_event & station_event) & ~nan_mask
    true_neg = (~satellite_event & ~station_event) & ~nan_mask

    counts = xr.Dataset(
        data_vars={
            'true_pos': true_pos,
            'false_pos': false_pos,
            'false_neg': false_neg,
            'true_neg': true_neg
        }
    )

    # group over time
    counts = groupby_time(counts, time_grouping=time_grouping, agg_fn='sum')
    # group over space
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)
    if region != 'global':
        mask_ds = clip_region(mask_ds, grid=grid, region=region)
    if not spatial:
        space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping, region=region).compute()
        if region != 'global':
            space_grouping_ds = clip_region(space_grouping_ds, grid=grid, region=region)

        counts = groupby_region(counts, space_grouping_ds, mask_ds, agg_fn='sum')
    else:
        counts = counts.where(mask_ds.mask, drop=False)

    # get rates
    tpr = counts['true_pos'] / (counts['true_pos'] + counts['false_neg'])
    fpr = counts['false_pos'] / (counts['false_pos'] + counts['true_neg'])

    auc = xr.apply_ufunc(np.trapezoid, tpr, fpr,
                         input_core_dims=[['threshold'], ['threshold']],
                         vectorize=True, dask='parallelized', output_dtypes=[float])
    import pdb; pdb.set_trace()

    return auc


__all__ = ['metric']
