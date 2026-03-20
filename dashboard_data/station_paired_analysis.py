"""Get gridded prodcuts by station locations."""
import xarray as xr
import numpy as np
from google.cloud import secretmanager
import pandas as pd
import dask

from nuthatch import cache, config_parameter
from sheerwater.utils import dask_remote, get_grid
from sheerwater.spatial_subdivisions import nonuniform_grid, is_station_grid
from sheerwater.interfaces import get_data
from sheerwater.masks import spatial_mask
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region, spacegrouping_category_codes
from sheerwater.utils.time_utils import assign_grouping_coordinates


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

        # We want to get the nearest grid point to the station, so we set tolerance
        # in the sel to the half width of the grid wel. For nonuniform grids like
        # SMAP, we use a fixed tolerance that's bigger than the smap size.
        try:
            _, _, grid_size, _ = get_grid(grid)
        except NotImplementedError:
            grid_size = 0.1

        ds = ds.sel(
            lat=station_df["lat"],
            lon=station_df["lon"],
            method="nearest",
            tolerance=grid_size/2 + 1e-6
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
                 grid='global0_25', mask='lsm', region='global', dropifnan=['tahmo_avg']):
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
    # drop rows where any of the dropifnan variables are NaN, so that we only have data where both TAHMO and the truth are available
    cols = []
    for source in dropifnan:
        variable = [variable for s, variable in sources if s == source]
        cols.append(f'{source}_{variable}')
    ds = ds.dropna("points", subset=dropifnan)

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.drop(columns=['time', 'lat', 'lon']).reset_index()
    return df

@cache(cache_args=["region", "space_grouping", "grid"], backend="sql")
def region_codes(start_time, end_time, estimate, truth, agg_days, grid, region="global", time_grouping="month_of_year", space_grouping="country"):
    bins = np.arange(0, 50, 1)
    hist2d = paired_histogram(start_time, end_time, estimate, truth, agg_days, variable='precip',
                              time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask='lsm', region=region, bins=bins, recompute=False)
    # get categories
    categories = hist2d.region.to_dask_dataframe().cat.categories
    # create pandas dataframe with region names and categories
    df = pd.DataFrame({"region": hist2d.region, "region_id": range(len(categories))})
    return df


@cache(cache_args=['estimate', 'truth', 'agg_days', 'grid', 'region'], backend='sql', backend_kwargs={'hash_table_name': False})
def hist_df(start_time, end_time, estimate, truth, agg_days, grid, region="global", time_grouping="month_of_year", space_grouping="country"):
    """Get a dataframe of the histogram data."""
    if agg_days <= 4:
        bins = np.arange(0, 100, 1)
    elif agg_days <= 7:
        bins = np.arange(0, 50, 1)
    else:
        bins = np.arange(0, 30, 1)
    hist2d = paired_histogram(start_time, end_time, estimate, truth, agg_days, variable='precip',
                              time_grouping=time_grouping, space_grouping=space_grouping, grid=grid, mask='lsm', region=region, bins=bins)
    # making this small enough to produce a pandas dataframe
    # make space grouping categorical
    region_codes = spacegrouping_category_codes(grid=grid, space_grouping=space_grouping, region=region)
    region_map = dict(zip(region_codes["region"], region_codes["region_id"]))
    hist2d = hist2d.assign_coords(region_id=("region", [region_map[r] for r in hist2d.region.values]))
    # swap region and region_id so we can drop region
    hist2d = hist2d.swap_dims({"region": "region_id"}).drop_vars("region")
    ddf = hist2d.to_dask_dataframe().reset_index()
    # drop zero bins
    ddf_sparse = ddf[ddf["precip"] > 0]
    # make time grouping categorical
    ddf_sparse["group"] = ddf_sparse["group"].astype("category")
    ddf_sparse = ddf_sparse.categorize(columns=["group"])
    ddf_sparse["group_id"] = ddf_sparse["group"].cat.codes
    ddf_sparse = ddf_sparse.drop(columns=["group"])
    # convert to pandas
    df = ddf_sparse.compute()
    df = df.drop(columns=['index'], errors='ignore')
    return df

@dask_remote
@cache(cache_args=['start_time', 'end_time', 'time_grouping', 'space_grouping', 'estimate', 'truth', 'agg_days', 'grid'])
def paired_histogram(start_time, end_time, estimate, truth, agg_days, variable='precip',
                     time_grouping=None, space_grouping=None, grid="global1_5", mask='lsm', region='global', spatial=False, bins=None):
    """Compute a paired histogram of two variables."""
    estimate_ds = get_data(estimate)(start_time, end_time, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
    truth_ds = get_data(truth)(start_time, end_time, variable, agg_days=agg_days, grid=grid, mask=mask, region=region)
    
    # align datasets
    estimate_ds, truth_ds = xr.align(estimate_ds, truth_ds, join='inner')
    # rename precip variables
    estimate_ds = estimate_ds.rename({'precip': 'estimate_precip'})
    truth_ds = truth_ds.rename({'precip': 'truth_precip'})
    # merge datasets on time and space
    merged_data = xr.merge([estimate_ds, truth_ds])

    # get bins of histogram
    if bins is None:
        max_value = 50
        step = 1
        bins = np.arange(0, max_value + step, step)
    
    hist2d = hist_grouping(merged_data, time_grouping, space_grouping, grid, mask, region, spatial,
    bins, variables=['estimate_precip', 'truth_precip'])
    # rename bin1 to estimate and bin2 to truth
    hist2d = hist2d.rename({'bin1': "estimate", 'bin2': "truth"})
    return hist2d


def hist_grouping(ds, time_grouping, space_grouping, grid, mask, region, spatial, bins, time_dim='time', **kwargs):
    """Group data into a histogram with optional time and space grouping."""
    def paired_hist(values1, values2, bins):
        mask = ~np.isnan(values1) & ~np.isnan(values2)
        values1 = values1[mask]
        values2 = values2[mask]

        hist2d, xedges, yedges = np.histogram2d(values1, values2, bins=bins)
        return hist2d

    # variables
    vars = kwargs.get("variables")
    # mask the data first
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)
    if region != 'global':
        mask_ds = clip_region(mask_ds, grid=grid, region=region)

    ds = ds.where(mask_ds.mask, drop=False)
    
    if time_grouping is None and space_grouping is None:
        ds = xr.apply_ufunc(paired_hist, ds[vars[0]], ds[vars[1]],
            input_core_dims=[[time_dim], [time_dim]], output_core_dims=[["bin1", "bin2"]],
            vectorize=True, dask="parallelized",
            output_dtypes=[int],
            dask_gufunc_kwargs={"allow_rechunk": True,
               "output_sizes": {"bin1": len(bins)-1, "bin2": len(bins)-1}},
            kwargs={"bins": bins},
        )
        ds = ds.assign_coords(bin1=bins[:-1], bin2=bins[:-1])
        ds = ds.to_dataset(name="precip")
    else:
        if time_grouping is not None:
        # add time and space grouping coordinates
            ds = assign_grouping_coordinates(ds, time_grouping, time_dim)
        if space_grouping is not None:
            space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping, region=region).compute()
            if region != 'global':
                space_grouping_ds = clip_region(space_grouping_ds, grid=grid, region=region)
            ds = ds.assign_coords(region=space_grouping_ds.region)
        time_groups = np.unique(ds.group.values)
        space_groups = np.unique(ds.region.values)
        hist_list = []
        for time_group in time_groups:
            for space_group in space_groups:
                ds_group = ds.where((ds.group == time_group) & (ds.region == space_group), drop=True)
                ds_group = xr.apply_ufunc(paired_hist, ds_group[vars[0]], ds_group[vars[1]],
                        input_core_dims=[[time_dim, 'lat', 'lon'], [time_dim, 'lat', 'lon']], output_core_dims=[["bin1", "bin2"]],
                        vectorize=False, dask="parallelized",
                        output_dtypes=[int],
                        dask_gufunc_kwargs={"allow_rechunk": True,
                            "output_sizes": {"bin1": len(bins)-1, "bin2": len(bins)-1}},
                        kwargs={"bins": bins},
                )
                ds_group = ds_group.assign_coords(bin1=bins[:-1], bin2=bins[:-1])
                ds_group = ds_group.expand_dims(group=[time_group], region=[space_group])
                ds_group = ds_group.to_dataset(name="precip")
                hist_list.append(ds_group)
        ds = xr.combine_by_coords(hist_list)
    return ds
