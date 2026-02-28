"""Get gridded prodcuts by station locations."""
import numpy as np
import xarray as xr
import xoak
import dask.dataframe as dd

from google.cloud import secretmanager

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote, get_grid
from sheerwater.spatial_subdivisions import nonuniform_grid, space_grouping_labels, clip_region
from sheerwater.data.tahmo import tahmo_deployment, tahmo_raw_daily
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


@dask_remote
@cache(cache_args=['data', 'station', 'grid'], backend='sql')
def data_at_stations(start_time, end_time, data='imerg', station='tahmo', grid='global0_1'):
    """Get a gridded data product at grid cells containing stations in tabular form.

    Args:
        start_time (str): The start time of the data.
        end_time (str): The end time of the data.
        data (str): The gridded data product to get the data from.
        station (str): The dataset to get the data from. Can be 'tahmo'.
            TODO: implement for GHCN, KNUST, etc. Need to get their station locations.
        grid (str): The grid to get the gridded data on.
    """
    # Select the station deployment locations
    if station == 'tahmo':
        # TODO: update this to use the source grid for all data sources
        station_df = tahmo_deployment().compute()
    else:
        raise ValueError(f"Invalid station dataset: {station}")

    # Get data source function
    data_fn = get_data(data)
    if 'smap' in data:
        variable = 'soil_moisture'
    else:
        variable = 'precip'
    ds = data_fn(start_time, end_time, variable=variable, grid=grid, agg_days=1, mask="lsm")
    if nonuniform_grid(ds) or grid == 'smap':
        # Set the index for lat and lon in a nonuniform grid
        ds = ds.set_xindex(("lat", "lon"), xr.indexes.NDPointIndex)

    # Calculate which grid points the stations are on, requires a uniform grid
    try:
        _, _, grid_size, _ = get_grid(grid)
    except NotImplementedError:
        grid_size = 0.05

    tab = ds.sel(
        lat=xr.DataArray(station_df["location_latitude"], dims="points"),
        lon=xr.DataArray(station_df["location_longitude"], dims="points"),
        method="nearest",
        tolerance=grid_size/2 + 1e-6
    )

    # Select those grid points from the satellite data
    tab = tab.to_dask_dataframe()
    tab = tab.drop(columns=['points'])
    # Drop columns where the variable is NaN
    tab = tab.dropna(subset=[variable])
    return tab


@dask_remote
@cache(cache_args=['station'], backend='sql')
def station_data(start_time, end_time, station='tahmo'):  # noqa: ARG001
    """Get a non-gridded, raw station data product.

    TODO: update this to use the source grid for all data sources
    """
    if station != 'tahmo':
        raise ValueError(f"Invalid station dataset: {station}")

    # Get TAHMO data by station ID and time
    df = tahmo_raw_daily()

    # Get TAHMO deployment locations
    df_dep = tahmo_deployment().compute()
    df_dep = df_dep[['code', 'location_latitude', 'location_longitude']]
    df_dep = df_dep.rename(columns={'code': 'station_id',
                                    'location_latitude': 'lat',
                                    'location_longitude': 'lon'})

    # Join the two dataframes on station ID
    df = df.merge(df_dep, on='station_id', how='left')
    return df


@cache(cache_args=['agg_days', 'grid', 'mask', 'region'], backend='sql')
def paried_data(start_time, end_time,
                sources=['rain_over_africa', 'chirps', 'imerg', 'tahmo', 'era5', 'era5'],
                variables=['precip', 'precip', 'precip', 'precip', 'tmp2m', 'rh2m'],
                agg_days=1,
                grid='global0_25', mask='lsm', region='global'):
    """Generate paired data at stations data for scatter plots."""
    datasets = [get_data(source)(start_time, end_time, variable, agg_days=agg_days,
                                 grid=grid, mask=mask, region=region)
                .rename({variable: f'{source}_{variable}'})
                for source, variable in zip(sources, variables)]

    # Get space grouping labels
    agzones = space_grouping_labels(grid=grid, space_grouping=['agroecological_zone', 'admin_1'])
    # clip agzones to the region
    agzones = clip_region(agzones, grid=grid, region=region)
    ds = xr.merge(datasets + [agzones])

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
    import pdb
    pdb.set_trace()

    return df


if __name__ == "__main__":
    from datetime import datetime
    from sheerwater.utils import start_remote
    start_remote(remote_name='genevieve')
    # start_remote()
    now = datetime.now().strftime("%Y-%m-%d")
    if True:
        # for grid in ['global0_1', 'global0_25', 'global1_5']:
        for grid in ['smap']:
            # for truth in ['smap_l4', 'chirps_v3', 'imerg_final', 'rain_over_africa']:
            for truth in ['smap_l3']:
                ds = data_at_stations(start_time='2015-01-01', end_time=now, data=truth,
                                      station='tahmo', grid=grid, backend='sql', recompute=True)

    if False:
        for grid in ['global0_1', 'global0_25', 'global1_5']:
            ds2 = paried_data(start_time='2015-01-01', end_time=now,
                              sources=['rain_over_africa', 'chirps_v3', 'imerg_final', 'tahmo', 'era5', 'era5'],
                              variables=['precip', 'precip', 'precip', 'precip', 'tmp2m', 'rh2m'],
                              agg_days=10,
                              grid=grid, mask='lsm', region='kenya', backend='sql')

    if False:
        ds3 = station_data(start_time='2015-01-01', end_time=now, station='tahmo')
    import pdb
    pdb.set_trace()
