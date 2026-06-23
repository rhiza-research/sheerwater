"""Cache climatology and annual series for dashboards."""
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from google.cloud import secretmanager

from nuthatch import cache
from nuthatch.config import config_parameter

from sheerwater.utils import start_remote
from sheerwater.climatology import climatology_agg_raw
from sheerwater.spatial_subdivisions import space_grouping_labels
from sheerwater.interfaces import get_data
from sheerwater.utils.data_utils import roll_and_agg

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

"""Precipitation climatology and annual series"""
@cache(cache_args=['data', 'region', 'grid'], backend='sql')
def get_precip_climatology(data, region, grid, mask='lsm', agg_days=5):
    ds = climatology_agg_raw('precip', data=data, region=region, grid=grid, mask=mask, agg_days=agg_days)
    df = ds.to_dataframe()
    df = df.reset_index()
    # drop lat / lon points where all values are NaN
    df = df.groupby(['lat', 'lon']).filter(lambda x: not x['precip'].isna().all())
    return df

@cache(cache_args=['region', 'data'], backend='sql')
def full_rainfall(start_time, end_time, data, region, grid="global0_25", mask="lsm", downsample=1):
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


"""Soil moisture climatology and annual series"""
@cache(cache_args=['region'], backend='sql')
def smap_climatology(start_time, end_time, region, mask="lsm"):
    ds = get_data("smap_l3")(start_time=start_time, end_time=end_time, grid="source", mask=mask)
    ds = frame_clip(ds, region)
    ds = roll_and_agg(ds, 5, agg_col="time", agg_fn='mean', agg_thresh=1)
    ds = ds.groupby("time.dayofyear").mean("time")

    df = ds.to_dataframe()
    df = df.reset_index()
    # drop y and x columns
    df = df.drop(columns=["y", "x"])
    # drop nan
    df = df.dropna(subset=["soil_moisture"])
    # round lat and lon to 2 decimal places
    df['lat'] = df['lat'].round(2)
    df['lon'] = df['lon'].round(2)

    return df

@cache(cache_args=['region'], backend='sql')
def full_smap(start_time, end_time, region, mask="lsm", downsample=1):
    ds = get_data("smap_l3")(start_time=start_time, end_time=end_time, grid="source", mask=mask)
    ds = frame_clip(ds, region)
    ds = roll_and_agg(ds, 5, agg_col="time", agg_fn='mean', agg_thresh=1)

    if downsample > 1:
        ds = ds.isel(
            x=slice(None, None, downsample),
            y=slice(None, None, downsample),
        )

    df = ds.to_dataframe()
    df = df.dropna(subset=["soil_moisture"])
    df = df.reset_index()
    # drop y and x columns
    df = df.drop(columns=["y", "x"])
    # round lat and lon to 2 decimal places
    df['lat'] = df['lat'].round(2)
    df['lon'] = df['lon'].round(2)
    return df

"""Utility functions"""
def frame_clip(ds, region):
    # clip crudely by lat / lon bounds for various regions
    if region == "western_africa":
        mask = (
            (ds.lat >= -5) & (ds.lat <= 25) &
            (ds.lon >= -20) & (ds.lon <= 15)
        )

    elif region == "eastern_africa":
        mask = (
            (ds.lat >= -30) & (ds.lat <= 30) &
            (ds.lon >= 20) & (ds.lon <= 50)
        )

    elif region == "india":
        mask = (
            (ds.lat >= 20) & (ds.lat <= 30) &
            (ds.lon >= 75) & (ds.lon <= 85)
        )

    else:
        raise ValueError(f"Unknown region: {region}")

    # Find bounding box in y/x space
    ys, xs = np.where(mask.compute())

    return ds.isel(
        y=slice(ys.min(), ys.max() + 1),
        x=slice(xs.min(), xs.max() + 1),
    )


if __name__ == "__main__":
    start_remote(remote_name='cache_climatology')

    start_time = '2015-01-01'
    end_time = '2025-12-31'

    #TODO: eastern africa has not been cached yet. 
    for region in ["india", "eastern_africa", "western_africa"]:

        """Cache soil moisture"""
        # climatology
        smap_climatology(start_time=start_time, end_time=end_time, region=region, mask='lsm')
        # annual series
        full_smap(start_time=start_time, end_time=end_time, region=region, mask='lsm', downsample=5)

        """Cache precipitation"""
        # climatology
        get_precip_climatology('imerg_final', region, 'global0_25')
        # annual series
        full_rainfall(start_time=start_time, end_time=end_time, data='imerg_final', region=region,
                      grid='global0_25', mask='lsm', downsample=5)

    """Cache rainfall region labels"""
    rainfall_region_labels('global0_25', recompute=['rainfall_region_labels', 'space_grouping_labels'])

    