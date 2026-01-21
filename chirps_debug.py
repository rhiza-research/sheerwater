from sheerwater.data.chirps import chirps, chirps_v2, chirps_gridded, chirps_v3
import matplotlib.pyplot as plt
from rasterio.transform import from_bounds
from sheerwater.utils.data_utils import regrid
from sheerwater.utils.region_utils import region_data
import xarray as xr
import shapely
from sheerwater.utils import start_remote
import numpy as np
from sheerwater.utils.space_utils import clip_with_mask
import matplotlib.pyplot as plt

def compare_grids(region="africa"):
    # Get CHIRPS data on CHIRPS grid
    chirps_data = chirps_v2(start_time="2020-01-01", end_time="2020-01-31", grid="chirps", region="global")

    # Get one day of CHIRPS
    chirps_day = chirps_data.precip.isel(time=0)
    # set crs and spatial dims but NO transform 
    chirps_day = chirps_day.rio.set_spatial_dims("lon", "lat")
    chirps_day = chirps_day.rio.write_crs("EPSG:4326")
    # get xarray lat lon points
    lat = chirps_day.lat.values
    lon = chirps_day.lon.values
    # get inferred lat lon points
    nx = len(lon)
    ny = len(lat)
    transform = chirps_day.rio.transform()
    lon_inferred = transform.c + transform.a * np.arange(nx)
    lat_inferred = transform.f + transform.e * np.arange(ny)

    # Plot
    step = 50
    X, Y = np.meshgrid(lat[::step], lon[::step])
    A, B = np.meshgrid(lat_inferred[::step], lon_inferred[::step])

    Xr, Yr = X.ravel(), Y.ravel()
    Ar, Br = A.ravel(), B.ravel()


    fig, axs = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
    axs[0].scatter(Xr, Yr, label="chirps", s=1)
    axs[0].legend()
    axs[1].scatter(Ar, Br, label="rectilinear", s=1)
    axs[1].legend()
    fig.suptitle(f"Chirps on chirps grid vs. rectilinear grid for {region}")
    import pdb; pdb.set_trace()
    plt.show()
    import pdb; pdb.set_trace()

def test_clipping(region="africa"):
    # get chirps data on chirps grid
    chirps_data = chirps(start_time="2020-01-01", end_time="2020-01-31", grid="chirps", region="global")
    region_df = region_data(region)
    
    # get a mask of the region
    lon2d, lat2d = xr.broadcast(
        chirps_data.lon,
        chirps_data.lat
    )
    lon2d, lat2d = lon2d.values, lat2d.values

    # set up the mask
    mask = np.zeros(lon2d.shape, dtype=bool)
    # filter first to the bounding box of the region
    polygon = region_df.geometry.union_all()
    bounds = polygon.bounds
    bmask = (lon2d >= bounds[0]) & (lon2d <= bounds[2]) & (lat2d >= bounds[1]) & (lat2d <= bounds[3])
    # filter next to precise polygon
    mask[bmask] = shapely.intersects_xy(polygon, lon2d[bmask], lat2d[bmask])
    # convert to x
    mask = xr.DataArray(mask, dims=("lon", "lat"), coords={"lon": chirps_data.lon, "lat": chirps_data.lat})
    import pdb; pdb.set_trace()
    chirps_clipped = chirps_data.where(mask)
    return chirps_clipped
    
def test_clipping_with_mask(region="africa", drop=True):
    # get chirps data on chirps grid
    chirps_data = chirps(start_time="2020-01-01", end_time="2020-01-31", grid="chirps", region="global")
    region_df = region_data(region)
    chirps_clipped = clip_with_mask(chirps_data, region_df, drop=drop)
    return chirps_clipped

def plot_with_latlon(ds, ax=None):
    da = ds.precip.isel(time=1)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    da.plot(ax=ax)

    # Draw latitude lines
    for lat in da.lat.values:
        ax.axhline(lat, color="k", linewidth=0.3, alpha=0.4)

    # Draw longitude lines
    for lon in da.lon.values:
        ax.axvline(lon, color="k", linewidth=0.3, alpha=0.4)

if __name__ == "__main__":
    start_remote(remote_name='mohini_chirps_debug')
    region="africa"
    
    start_time = "2020-01-01"
    end_time = "2020-01-31"
    ds = chirps_gridded(start_time, end_time, grid="chirps", version=3, stations=True)
    region_df = region_data(region)
    d1 = clip_with_mask(ds, region_df, drop=True)
    import pdb; pdb.set_trace()
    d1.precip.isel(time=0).plot()
    """
    d2 = clip_with_mask(ds, region_df, drop=False)
    # clip with rio
    d3 = ds.rio.write_crs("EPSG:4326")
    d3 = d3.rio.set_spatial_dims("lon", "lat")
    # Clip the grid to the boundary of Shapefile
    d3 = d3.rio.clip(region_df.geometry, region_df.crs, drop=True)
    import pdb; pdb.set_trace()
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    plot_with_latlon(d1, ax=axs[0])
    plot_with_latlon(d2, ax=axs[1])
    plt.show()
    import pdb; pdb.set_trace()"""