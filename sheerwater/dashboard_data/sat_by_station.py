from datetime import datetime

import dask.dataframe as dd
from nuthatch import cache
from sheerwater.utils import dask_remote, snap_point_to_grid, get_grid, start_remote

from sheerwater.data.tahmo import tahmo_deployment

from sheerwater.interfaces import get_data


@dask_remote
@cache(cache_args=['satellite', 'station', 'grid'], backend='sql')
def sat_station(satellite='imerg', station='tahmo', grid='imerg'):
    """Get the IMERG data at the station locations.

    Args:
        satellite (str): The satellite to get the data from. Can be 'imerg', 'chirps'.
        station (str): The dataset to get the data from. Can be 'tahmo'.
            TODO: implement for GHCN, KNUST, etc.
        grid (str): The grid to get the data from.
    """
    # Get satellite source function
    sat_fn = get_data(satellite)
    now = datetime.now().strftime("%Y-%m-%d")
    ds = sat_fn("2015-01-01", now, variable="precip", grid=grid, agg_days=1, mask="lsm")

    # Select the station deployment
    if station == 'tahmo':
        df = tahmo_deployment().compute()
    else:
        raise ValueError(f"Invalid station dataset: {station}")

    # Get which grid points the stations are in
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


if __name__ == "__main__":
    from sheerwater.dashboard_data import sat_station
    start_remote()
    sat_station(satellite='chirps_v3', station='tahmo', grid='chirps', backend='sql')
