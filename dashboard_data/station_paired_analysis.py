"""Get gridded prodcuts by station locations."""
import xarray as xr
import numpy as np
from google.cloud import secretmanager

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote, get_grid
from sheerwater.spatial_subdivisions import nonuniform_grid, space_grouping_labels, clip_region, is_station_grid
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
@cache(cache_args=['start_time', 'end_time', 'data', 'station', 'grid'], backend='sql')
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
    # Get the station data on the source grid
    station_fn = get_data(station)
    station_df = station_fn(start_time, end_time, variable='precip', grid='source', agg_days=1, mask="lsm")
    if not is_station_grid(station_df):
        raise ValueError(f"Station grid {station_df} is not a station grid")

    # Get data source function
    variable = 'precip' if 'smap' not in data else 'soil_moisture'
    data_fn = get_data(data)
    ds = data_fn(start_time, end_time, variable=variable, grid=grid, agg_days=1, mask="lsm")
    if nonuniform_grid(ds):
        # Set the index for lat and lon in a nonuniform grid
        ds = ds.set_xindex(("lat", "lon"), xr.indexes.NDPointIndex)

    # Calculate which grid points the stations are on, requires a uniform grid
    try:
        _, _, grid_size, _ = get_grid(grid)
    except NotImplementedError:
        grid_size = 0.05

    tab = ds.sel(
        lat=station_df["lat"],
        lon=station_df["lon"],
        method="nearest",
        tolerance=grid_size/2 + 1e-6
    )

    # Select those grid points from the satellite data
    tab = tab.to_dask_dataframe()
    tab = tab.drop(columns=['station_id'])
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
    station_fn = get_data(station)
    station_df = station_fn(start_time, end_time, variable='precip', grid='source', agg_days=1, mask="lsm")
    if not is_station_grid(station_df):
        raise ValueError(f"Station grid {station_df} is not a station grid")
    return station_df


@cache(cache_args=['agg_days', 'grid', 'mask', 'region'], backend='sql')
def paried_data(start_time, end_time,
                sources=[('rain_over_africa', 'precip'), ('chirps_v3', 'precip'), ('imerg_final', 'precip'),
                         ('tahmo_avg', 'precip'), ('era5', 'tmp2m'), ('era5', 'rh2m')],
                agg_days=1,
                grid='global0_25', mask='lsm', region='global'):
    """Generate paired data at stations data for scatter plots."""
    datasets = [get_data(source)(start_time, end_time, variable=variable, agg_days=agg_days,
                                 grid=grid if 'smap' not in source else 'source',
                                 mask=mask, region=region)
                .rename({variable: f'{source}_{variable}'})
                for source, variable in sources]

    # Ensure that lat and lon are rounded to 5 decimal places and cast as float32 so the merging doesn't fail
    for ds in datasets:
        ds['lat'] = ds['lat'].round(5).astype(np.float32)
        ds['lon'] = ds['lon'].round(5).astype(np.float32)
    ds = xr.merge(datasets)

    # Assign country coordinate values to the main dataset
    # country_ds = space_grouping_labels(grid=grid, space_grouping=['country'])
    # country_ds = clip_region(country_ds, grid=grid, region=region)
    # ds = ds.assign_coords(country=(('lat', 'lon'), country_ds['region'].values))

    # stack into a table
    ds = ds.stack(points=("time", "lat", "lon"))
    # drop rows where 'tahmo_avg_precip' is NaN
    ds = ds.dropna("points", subset=["tahmo_avg_precip"])

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.drop(columns=['time', 'lat', 'lon']).reset_index()
    return df


if __name__ == "__main__":
    from datetime import datetime
    from sheerwater.utils import start_remote
    # start_remote(remote_name='genevieve')
    start_remote()
    now = datetime.now().strftime("%Y-%m-%d")
    if False:
        variable = 'precip'
        for truth in ['smap_l3', 'chirps_v3', 'imerg_final', 'rain_over_africa']:
            for grid in ['global0_1', 'global0_25', 'global1_5']:
                if 'smap' in truth and grid == 'global0_1':
                    # Hard code source grid and soil moisture variable for smap
                    ds = data_at_stations(start_time='2015-01-01', end_time=now, data=truth,
                                          station='stations', grid='source', backend='sql')
                elif 'smap' not in truth:
                    # Otherwise, use the regular grid
                    ds = data_at_stations(start_time='2015-01-01', end_time=now, data=truth,
                                          station='stations', grid=grid, backend='sql')

    if True:
        for grid in ['global0_1', 'global0_25', 'global1_5']:
            for region in ['ghana', 'kenya']:
                for agg_days in [1, 5, 10]:
                    sources = [('rain_over_africa', 'precip'),
                               ('chirps_v3', 'precip'),
                               ('imerg_final', 'precip'),
                               ('tahmo_avg', 'precip')]
                    if grid in ['global0_25', 'global1_5']:
                        # ERA5 is only available on global0_25 and global1_5
                        # sources.append(('era5', 'tmp2m'))
                        # sources.append(('era5', 'rh2m'))
                        pass

                    ds2 = paried_data(start_time='2015-01-01', end_time=now,
                                      sources=sources,
                                      agg_days=agg_days,
                                      grid=grid, mask='lsm', region=region, backend='sql')

    if False:
        ds3 = station_data(start_time='2015-01-01', end_time=now, station='tahmo')
    import pdb
    pdb.set_trace()
