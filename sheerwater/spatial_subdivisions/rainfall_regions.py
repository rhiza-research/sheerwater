"""Rainfall region clustering."""
import pandas as pd
import numpy as np
import xarray as xr

from nuthatch import cache
from sheerwater.utils import get_grid
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

def rescale(df, mode="min-max"):
    """Rescale the data to a range of 0-1 or -1-1."""
    if mode == "min-max":
        row_min = np.nanmin(df.values, axis=1, keepdims=True)
        row_max = np.nanmax(df.values, axis=1, keepdims=True)
        denom = np.where((row_max - row_min) == 0, 1, row_max - row_min)
        scaled = (df.values - row_min) / denom

    elif mode == "z-score":
        mean = df.values.mean(axis=1, keepdims=True)
        std = df.values.std(axis=1, keepdims=True)
        std = np.where(std == 0, 1, std)
        scaled = (df.values - mean) / std

    else:
        raise ValueError(f"Invalid mode: {mode}")

    return pd.DataFrame(
        scaled,
        index=df.index,
        columns=df.columns
    )


@cache(cache_args=['data_source', 'kregions', 'region', 'grid', 'agg_days', 'smooth_neighbors', 'spatial_coherence'])
def get_rainfall_regions(data_source, kregions=5, region="africa", grid="global0_25", mask="lsm",
                         agg_days=1, smooth_neighbors=50, spatial_coherence=0.0):
    """Cluster grid cells by precipitation climatology into kregions."""
    from sheerwater.climatology import climatology
    # time range of climatology (years don't matter)
    start_time, end_time = "1979-01-01", "1979-12-31"
    # years over which to compute the climatology
    first_year, last_year = 2015, 2025
    # get the annual climatology for the region
    clim_ds = climatology(start_time, end_time, "precip", agg_days, data=data_source,
                          first_year=first_year, last_year=last_year,
                          grid=grid, mask=mask, region=region,
                          prob_type='deterministic', trend=False)

    # prepare data for clustering
    df = clim_ds.to_dataframe()
    df = df.reset_index()
    df['time'] = pd.to_datetime(df['time'])
    df['point_id'] = list(zip(df['lat'], df['lon']))
    # pivot - rows are points, columns are times, values are precip
    df = df.pivot_table(index='point_id', columns='time', values='precip').sort_index(axis=1)
    df = df.fillna(0)

    df = rescale(df, mode="min-max")

    if spatial_coherence > 0.0:
        # add lat, lon as features to encourage spatial coherence of clusters
        # spatial features
        lat = np.array([x[0] for x in df.index])
        lon = np.array([x[1] for x in df.index])

        spatial_features = np.column_stack([lat, lon])

        # normalize spatial coords
        spatial_features = StandardScaler().fit_transform(spatial_features)

        # combine rainfall + spatial features
        df["lat"] = spatial_features[:, 0]
        df["lon"] = spatial_features[:, 1]


    # run k-means clustering
    kmeans = KMeans(n_clusters=kregions, random_state=42, n_init=10)
    labels = kmeans.fit_predict(df.values)
    # prepare cluster dataframe
    lat = np.array([coords[0] for coords in df.index.tolist()])
    lon = np.array([coords[1] for coords in df.index.tolist()])

    # use k-nearest neighbors to make clusters more contiguous
    knn = KNeighborsClassifier(n_neighbors=smooth_neighbors)
    locs = np.column_stack([lat, lon])
    knn.fit(locs, labels)
    cleaned_labels = knn.predict(locs)

    # create masks for each cluster
    g_lons, g_lats, _, _ = get_grid(grid)
    ds_regions = xr.DataArray(
        np.zeros((len(g_lats), len(g_lons), kregions), dtype=bool),
        coords={"lat": g_lats, "lon": g_lons, "region": range(kregions)},
        dims=["lat", "lon", "region"],
        name="masks"
    )
    for region_idx in range(kregions):
        region_lat, region_lon = lat[cleaned_labels == region_idx], lon[cleaned_labels == region_idx]
        for rlat, rlon in zip(region_lat, region_lon):
            ds_regions.loc[{"lat": rlat, "lon": rlon, "region": region_idx}] = True

    return ds_regions



