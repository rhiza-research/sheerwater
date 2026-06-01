import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

from nuthatch import cache
from nuthatch.config import config_parameter
from google.cloud import secretmanager
from sheerwater.utils import start_remote, dask_remote
from sheerwater.climatology import climatology_agg_raw
from dashboard_data.station_paired_analysis import scatter_data
from sheerwater.spatial_subdivisions import space_grouping_labels
from sheerwater.interfaces import get_data

# Add the postgres write password to the config parameter, so that this code
# module can read and write to our postgres database.
@config_parameter('password', location='root', backend='sql', secret=True)
def postgres_write_password():
    """Get a postgres write password."""
    client = secretmanager.SecretManagerServiceClient()

    response = client.access_secret_version(
        request={"name": "projects/750045969992/secrets/postgres-write-password/versions/latest"})
    key = response.payload.data.decode("UTF-8")

    return key


@cache(cache_args=['data', 'region', 'grid'], backend='sql')
def get_precip_climatology(data, region, grid, mask='lsm', agg_days=5):
    ds = climatology_agg_raw('precip', data=data, region=region, grid=grid, mask=mask, agg_days=agg_days)
    df = ds.to_dataframe()
    df = df.reset_index()
    # drop lat / lon points where all values are NaN
    df = df.groupby(['lat', 'lon']).filter(lambda x: not x['precip'].isna().all())
    return df

@cache(cache_args=['grid'], backend='sql')
def rainfall_region_labels(grid):
    rainfall_regions = space_grouping_labels(grid=grid, space_grouping='rainfall_region')
    rainfall_regions = rainfall_regions.drop_vars('rainfall_region_region').region
    rainfall_regions = rainfall_regions.drop_vars('region')
    df = rainfall_regions.to_dataframe()
    df = df.reset_index()
    # drop all rows where region is no_region
    df = df[df['region'] != 'no_region']
    return df

@cache(cache_args=['region', 'data'], backend='sql')
def raw_timeseries(start_time, end_time, data, region, grid="global0_25", mask="lsm", downsample=1):
    ds = get_data(data)(start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)

    if downsample > 1:
            ds = ds.isel(
                lat=slice(None, None, downsample),
                lon=slice(None, None, downsample),
            )

    df = ds.to_dataframe()
    # drop rows where precip is NaN
    df = df.dropna(subset=["precip"])
    df = df.reset_index()
    # for testing - get first 100 rows of df
    df = df.head(100)
    import pdb; pdb.set_trace()

    return df

if __name__ == "__main__":
    start_remote(remote_name='mohini_onset_defs')
    raw_timeseries(start_time='2015-01-01', end_time='2025-12-31', data='imerg_final', region='india',
    grid='global0_25', mask='lsm', downsample=10)
    import pdb; pdb.set_trace()

    #from sheerwater.spatial_subdivisions.spatial_subdivisions import rainfall_region_labels
    #rr = rainfall_region_labels('global0_25', recompute=True)
    #)


    rainfall_region_labels('global0_25', recompute=['rainfall_region_labels', 'space_grouping_labels'])
    #scatter_data(start_time='2020-01-01', end_time='2020-02-20', recompute=True)
    import pdb; pdb.set_trace()

    # precipitation
    #get_precip_climatology('imerg_final', 'india', 'global0_25')
    #get_precip_climatology('imerg_final', 'eastern_africa', 'global0_25')
    #get_precip_climatology('imerg_final', 'western_africa', 'global0_25')

    