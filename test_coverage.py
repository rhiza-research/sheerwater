from sheerwater.metrics import coverage
from sheerwater.utils import start_remote

import xarray as xr
from nuthatch import cache

from sheerwater.metrics_library import metric_factory
from sheerwater.interfaces import get_data
from sheerwater.regions_and_masks import region_labels, spatial_mask
from sheerwater.utils import dask_remote, groupby_region, groupby_time, clip_region

import matplotlib.pyplot as plt


def get_coverage(start_time=None, end_time=None, variable='precip', agg_days=7, station_data='ghcn_avg',
             time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm',
             region='global'):
             # get station data
    """Compute coverage of a dataset."""
    # Get the station data over the desired period
    station_data_fn = get_data(station_data)
    data = station_data_fn(start_time, end_time, variable, agg_days=agg_days,
                           grid='global1_5', region=region)

    # indicate time/space points that are not null (ie adequate coverage)
    data['non_null'] = data[variable].notnull()
    # indicator at every time/space point
    data['indicator'] = xr.ones_like(data[variable])

    # get mean over time
    data_tm = groupby_time(data, time_grouping=time_grouping, agg_fn='mean')
    data_ts = groupby_time(data, time_grouping=time_grouping, agg_fn='sum')
    import pdb; pdb.set_trace()

    # mask the data
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)
    if region != 'global':
        mask_ds = clip_region(mask_ds, region=region)

    region_ds = region_labels(grid=grid, space_grouping=space_grouping, region=region).compute()
    data_tm = groupby_region(data_tm, region_ds, mask_ds, agg_fn='sum')
    data_ts = groupby_region(data_ts, region_ds, mask_ds, agg_fn='sum')

    data['coverage'] = data['non_null'] / data['indicator']

    data = data.drop_vars(variable)
    return data


if __name__ == "__main__":
    start_remote(remote_config='large_cluster')

    # arguments for coverage
    start_time = "2020-01-01"
    end_time = "2020-03-01"
    variable = "precip"
    agg_days = 7
    station_data = "ghcn_avg"
    time_grouping = "month"
    space_grouping = "country"
    grid = "global1_5"
    mask = "lsm"
    region = "africa"
    ds = coverage(start_time=start_time, end_time=end_time, variable=variable, agg_days=agg_days, 
    station_data=station_data, time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask=mask, region=region)

    #ds = get_coverage(start_time, end_time, variable=variable, agg_days=agg_days, 
    #station_data=station_data, time_grouping=time_grouping, grid=grid, mask=mask, region=region)