"""Verification metrics for forecasters and reanalyses."""
import xarray as xr
from nuthatch import cache
import warnings
import numpy as np

from sheerwater.metrics_library import metric_factory
from sheerwater.interfaces import get_data
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region
from sheerwater.masks import spatial_mask
from sheerwater.utils import dask_remote, groupby_region, groupby_time
from sheerwater.utils import time_utils
from sheerwater.utils import assign_grouping_coordinates


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
           spatial=False, grid="global1_5", mask='lsm', region='global', memoize_forecast=True, memoize_truth=True):
    """Compute a grouped metric for a forecast at a specific lead."""
    # Use the metric registry to get the metric class
    metric_obj = metric_factory(metric_name, start_time=start_time, end_time=end_time, variable=variable,
                                agg_days=agg_days, forecast=forecast, truth=truth, time_grouping=time_grouping,
                                space_grouping=space_grouping, spatial=spatial, grid=grid, mask=mask, region=region,
                                memoize_forecast=memoize_forecast, memoize_truth=memoize_truth)
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
@cache(cache_args=['start_time', 'end_time', 'time_grouping', 'space_grouping', 'estimate', 'truth', 'agg_days', 'grid'])
def paired_histogram(start_time, end_time, estimate, truth, agg_days, variable='precip',
    time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global', spatial=False, bins=None):
    """Compute a paired histogram of two variables."""
    estimate = get_data(estimate)(start_time, end_time, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
    truth = get_data(truth)(start_time, end_time, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
    
    # align datasets
    estimate, truth = xr.align(estimate, truth, join='inner')
    # rename precip variables
    estimate = estimate.rename({'precip': 'estimate_precip'})
    truth = truth.rename({'precip': 'truth_precip'})
    # merge datasets on time and space
    merged_data = xr.merge([estimate, truth])

    # get bins of histogram
    if bins is None:
        max_value = 50
        step = 5
        bins = np.arange(0, max_value + step, step)
    
    hist2d = hist_grouping(merged_data, time_grouping, space_grouping, grid, mask, region, spatial,
    bins, variables=['estimate_precip', 'truth_precip'])

    return hist2d

def hist_grouping(ds, time_grouping, space_grouping, grid, mask, region, spatial, bins, time_dim='time', **kwargs):
    """Group a histogram by time and space."""
    def paired_hist(values1, values2, bins):
        mask = ~np.isnan(values1) & ~np.isnan(values2)
        values1 = values1[mask]
        values2 = values2[mask]

        hist2d, xedges, yedges = np.histogram2d(values1, values2, bins=bins)
        return hist2d

    # variables
    vars = kwargs.get("variables")
    # mask the data first
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)
    if region != 'global':
        mask_ds = clip_region(mask_ds, grid=grid, region=region)

    ds = ds.where(mask_ds.mask, drop=False)
    
    if time_grouping is None and space_grouping is None:
        ds = xr.apply_ufunc(paired_hist, ds[vars[0]], ds[vars[1]],
            input_core_dims=[[time_dim], [time_dim]], output_core_dims=[["bin1", "bin2"]],
            vectorize=True, dask="parallelized",
            output_dtypes=[int],
            dask_gufunc_kwargs={"allow_rechunk": True},
            output_sizes={"bin1": len(bins)-1, "bin2": len(bins)-1},
            kwargs={"bins": bins},
        )
        ds = ds.assign_coords(bin1=bins[:-1], bin2=bins[:-1])
        ds = ds.to_dataset(name="precip")
    else:
        if time_grouping is not None:
        # add time and space grouping coordinates
            ds = assign_grouping_coordinates(ds, time_grouping, time_dim)
        if space_grouping is not None:
            space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping, region=region).compute()
            if region != 'global':
                space_grouping_ds = clip_region(space_grouping_ds, grid=grid, region=region)
            ds = ds.assign_coords(region=space_grouping_ds.region)
        time_groups = np.unique(ds.group.values)
        space_groups = np.unique(ds.region.values)
        hist_list = []
        for time_group in time_groups:
            for space_group in space_groups:
                ds_group = ds.where((ds.group == time_group) & (ds.region == space_group), drop=True)
                ds_group = xr.apply_ufunc(paired_hist, ds_group[vars[0]], ds_group[vars[1]],
                        input_core_dims=[[time_dim, 'lat', 'lon'], [time_dim, 'lat', 'lon']], output_core_dims=[["bin1", "bin2"]],
                        vectorize=False, dask="parallelized",
                        output_dtypes=[int],
                        dask_gufunc_kwargs={"allow_rechunk": True},
                        output_sizes={"bin1": len(bins)-1, "bin2": len(bins)-1},
                        kwargs={"bins": bins},
                )
                ds_group = ds_group.assign_coords(bin1=bins[:-1], bin2=bins[:-1])
                ds_group = ds_group.expand_dims(group=[time_group], region=[space_group])
                ds_group = ds_group.to_dataset(name="precip")
                hist_list.append(ds_group)
        import pdb; pdb.set_trace()
        ds = xr.combine_by_coords(hist_list)
    return ds

__all__ = ['metric', 'paired_histogram', 'hist_grouping']
