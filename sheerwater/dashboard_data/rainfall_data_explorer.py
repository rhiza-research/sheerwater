"""Cache tables in postgres for the SPW dashboard."""
import numpy as np
import xarray as xr

from nuthatch import cache
from sheerwater.utils import dask_remote, start_remote, get_grid, snap_point_to_grid
from sheerwater.interfaces import get_data
from sheerwater.data.tahmo import tahmo_deployment


@dask_remote
@cache(cache_args=['grid'], backend='sql')
def tahmo_grid_counts(grid='global0_25'):
    """Get the TAHMO stations and counts of stations per grid cell."""
    # Round the coordinates to the nearest grid
    _, _, grid_size, offset = get_grid(grid)

    # Get TAHMO deployment over all time
    stations = tahmo_deployment().compute()
    stat = stations.rename(columns={'location_latitude': 'lat', 'location_longitude': 'lon', 'code': 'station_id'})
    stat['lat'] = stat['lat'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    stat['lon'] = stat['lon'].apply(lambda x: snap_point_to_grid(x, grid_size, offset))

    stat = stat[['station_id', 'lat', 'lon']]
    # count the number of stations in each grid cell & make new column with list of station ids
    sparse_counts = stat.groupby(['lat', 'lon']).agg(station_ids=('station_id', 'unique'),
                                                     counts=('station_id', 'size'))

    # Explode the station_ids column into a list of station ids
    sparse_counts = sparse_counts.explode('station_ids')
    sparse_counts = sparse_counts.reset_index()
    return sparse_counts


@dask_remote
@cache(backend='sql',
       cache_args=['agg_days', 'grid', 'mask', 'region'])
def rainfall_data(start_time, end_time, agg_days=1,
                  grid='global1_5', mask='lsm', region='global'):
    """Store rainfall data across data sources to the database."""
    # Get the ground truth data
    datasets = []
    import pdb
    pdb.set_trace()
    truth = ['era5', 'chirps', 'imerg', 'ghcn', 'tahmo', 'knust']
    for truth in truth:
        source_fn = get_data(truth)
        ds = source_fn(start_time, end_time, 'precip', agg_days=agg_days,
                       grid=grid, mask=mask, region=region)
        ds = ds.rename({'precip': f'{truth}_precip'})
        datasets.append(ds)

    # Merge datasets
    ds = xr.merge(datasets, join='outer')
    ds = ds.drop_vars(['number', 'spatial_ref'])

    # Convert to dataframe
    df = ds.to_dataframe()
    return df


if __name__ == "__main__":
    start_remote()
    grid_counts = tahmo_grid_counts(grid='global0_25', backend='sql')
    # start_time = '2022-01-01'
    # end_time = '2024-12-31'
    # agg_days = [1]
    # for agg_day in agg_days:
    #     ds = rainfall_data(start_time, end_time, agg_day, grid='global0_25', mask='lsm', region='africa')
