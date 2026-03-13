"""Get gridded prodcuts by station locations."""
import xarray as xr
import numpy as np
from google.cloud import secretmanager

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote
from sheerwater.spatial_subdivisions import nonuniform_grid, is_station_grid
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
@cache(cache_args=['data', 'station', 'grid', 'variable', 'agg_days'], backend='sql')
def data_at_stations(start_time, end_time, data='imerg', variable='precip', agg_days=1,
                     station='tahmo', grid='global0_1'):
    """Get a gridded data product at grid cells containing stations in tabular form.

    If a station dataset is provided in the data argument, the station data is converted
    to a dataframe and returned directly and the station argument is not used.

    Args:
        start_time (str): The start time of the data.
        end_time (str): The end time of the data.
        data (str): The gridded data product to get the data from.
        station (str): The dataset to get the data from. Can be any valid station dataset, 
        including 'tahmo', 'knust', 'ghcn', 'stations', etc.
        variable (str): The variable to get the data from. Can be 'precip' or 'soil_moisture'.
        agg_days (int): The number of days to aggregate the data over.
        grid (str): The grid to get the gridded data on.
    """
    # Get data source function
    data_fn = get_data(data)
    ds = data_fn(start_time, end_time, variable=variable, grid=grid, agg_days=agg_days, mask="lsm")

    if not is_station_grid(ds):
        # Get the station data on the source grid to determine which grid points the stations are on
        # This data is not piped through to the final data product
        station_fn = get_data(station)
        station_df = station_fn(start_time, end_time, variable='precip', grid='source', agg_days=agg_days, mask="lsm")
        if not is_station_grid(station_df):
            raise ValueError(f"Station grid {station_df} is not a station grid")

        if nonuniform_grid(ds):
            # Set the index for lat and lon in a nonuniform grid
            ds = ds.set_xindex(("lat", "lon"), xr.indexes.NDPointIndex)

        # Get the grid size to ensure that only one nearest neigthbor
        ds = ds.sel(
            lat=station_df["lat"],
            lon=station_df["lon"],
            method="nearest",
            tolerance=2.0
        )

    # Select those grid points from the satellite data
    tab = ds.to_dask_dataframe()
    # Drop columns where the variable is NaN
    tab = tab.dropna(subset=[variable])
    return tab


@cache(cache_args=['agg_days', 'grid', 'mask', 'region'], backend='sql')
def scatter_data(start_time, end_time,
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
    # drop rows where 'tahmo_avg_precip' is NaN, so that we only have data where both TAHMO and the truth are available
    ds = ds.dropna("points", subset=["tahmo_avg_precip"])

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.drop(columns=['time', 'lat', 'lon']).reset_index()
    return df
