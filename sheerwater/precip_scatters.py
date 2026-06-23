import xarray as xr
from sheerwater.interfaces import get_data
import matplotlib.pyplot as plt
from sheerwater.utils import start_remote
from scipy.stats import gaussian_kde
import numpy as np
import scipy.stats
from nuthatch import cache
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region
from sheerwater.reanalysis.era5 import era5

# make this a cacheable function
@cache(cache_args=['agg_days', 'grid', 'precip1', 'precip2', 'region'], backend='sql')
def pairwise_precip(start_time, end_time, precip1, precip2, agg_days, grid='global0_25', mask='lsm', region='global'):
    
    ds1 = get_data(precip1)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)
    ds2 = get_data(precip2)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)

    ds1 = ds1.rename({'precip': f'{precip1}_precip'})
    ds2 = ds2.rename({'precip': f'{precip2}_precip'})

    # get temperature & humidity from ERA5
    tmp_ds = era5(start_time, end_time, 'tmp2m', agg_days=agg_days, grid=grid, mask=mask, region=region)
    rh_ds = era5(start_time, end_time, 'rh2m', agg_days=agg_days, grid=grid, mask=mask, region=region)

    # get space_grouping labels
    agzones = space_grouping_labels(grid=grid, space_grouping=['agroecological_zone', 'admin_1'])
    # clip agzones to the region
    agzones = clip_region(agzones, grid=grid, region=region)
    ds = xr.merge([ds1, ds2, rh_ds, tmp_ds, agzones])

    # drop variable mask & region coordinates
    ds = ds.drop_vars(['mask', 'region'])
    # move admin_1_region and agroecological_zone_region from coords to variables
    ds = ds.reset_coords(['admin_1_region', 'agroecological_zone_region'])

    # stack into a table
    ds = ds.stack(points=("time", "lat", "lon"))
    # drop coords and variables that are not needed
    ds = ds.dropna("points")

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.drop(columns=['time', 'lat', 'lon', 'spatial_ref']).reset_index()

    return df