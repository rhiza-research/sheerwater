"""Get gridded prodcuts by station locations."""
import xarray as xr
import dask.dataframe as dd

from google.cloud import secretmanager

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote, snap_point_to_grid, get_grid
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
def data_at_stations(start_time, end_time, data='imerg', station='tahmo', grid='imerg'):
    """Get a gridded data product at the station locations.

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
        df = tahmo_deployment().compute()
    else:
        raise ValueError(f"Invalid station dataset: {station}")

    # Get data source function
    data_fn = get_data(data)
    ds = data_fn(start_time, end_time, variable="precip", grid=grid, agg_days=1, mask="lsm")
    if nonuniform_grid(ds):
        raise ValueError("Grid is nonuniform. Cannot calculate grid points for stations.")

    # Calculate which grid points the stations are on, requires a uniform grid
    _, _, grid_size, offset = get_grid(grid)
    df["location_latitude"] = df["location_latitude"].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    df["location_longitude"] = df["location_longitude"].apply(lambda x: snap_point_to_grid(x, grid_size, offset))
    lats = df["location_latitude"].unique()
    lons = df["location_longitude"].unique()

    # Select those grid points from the satellite data
    ds = ds.sel(lat=lats, lon=lons, method="nearest", tolerance=0.001)
    ds = ds.to_dask_dataframe()

    # Get grid index for joining (more numerically stable than using lat/lon)
    ds['lat_index'] = (ds['lat']/grid_size).astype("int32")
    ds['lon_index'] = (ds['lon']/grid_size).astype("int32")

    # Join to filter
    df_filt = df[["location_latitude", "location_longitude", "code"]]
    df_filt["location_latitude"] = df_filt["location_latitude"].astype("float32")
    df_filt["location_longitude"] = df_filt["location_longitude"].astype("float32")
    df_filt["lat_index"] = (df_filt["location_latitude"]/grid_size).astype("int32")
    df_filt["lon_index"] = (df_filt["location_longitude"]/grid_size).astype("int32")

    # Join on index
    ds = dd.merge(ds, df_filt, on=["lat_index", "lon_index"], how="inner")

    # Drop index columns
    ds = ds.drop(columns=["lat_index", "lon_index", "location_latitude", "location_longitude"])
    return ds


@dask_remote
@cache(cache_args=['station'], backend='sql')
def station_data(start_time, end_time, station='tahmo'):
    """Get a non-gridded, raw station data product."""
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


@cache(cache_args=['sources', 'variables', 'agg_days', 'grid', 'mask', 'region'], backend='sql')
def paried_data(start_time, end_time,
                sources=['chirps', 'imerg', 'tahmo', 'era5', 'era5'],
                variables=['precip', 'precip', 'precip', 'tmp2m', 'rh2m'],
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

    return df


if __name__ == "__main__":
    from datetime import datetime
    from sheerwater.utils import start_remote
    start_remote()
    now = datetime.now().strftime("%Y-%m-%d")
    # ds1 = data_at_stations(start_time='2015-01-01', end_time=now, data='imerg_final',
    #                        station='tahmo', grid='imerg', backend='sql')

    # ds2 = paried_data(start_time='2015-01-01', end_time=now,
    #                   sources=['chirps_v3', 'imerg', 'tahmo', 'era5', 'era5'],
    #                   variables=['precip', 'precip', 'precip', 'tmp2m', 'rh2m'],
    #                   agg_days=1,
    #                   grid='imerg', mask='lsm', region='kenya', backend='sql')

    ds3 = station_data(start_time='2015-01-01', end_time=now, station='tahmo')
    import pdb; pdb.set_trace()
