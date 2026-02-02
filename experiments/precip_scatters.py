import xarray as xr
from sheerwater.interfaces import get_data
import matplotlib.pyplot as plt
from sheerwater.utils import start_remote
from scipy.stats import gaussian_kde
import numpy as np
import scipy.stats
from nuthatch import cache
from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region
from sheerwater.reanalysis.era5 import era5

# make this a cacheable function
#@cache(cache_args=['agg_days', 'grid', 'x_source', 'y_source', 'region], backend='sql')
def pairwise_precip(start_time, end_time, x_source, y_source, agg_days, grid='global0_25', mask='lsm', region='global'):
    
    x_ds = get_data(x_source)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)
    y_ds = get_data(y_source)(start_time, end_time, 'precip', agg_days=agg_days, grid=grid, mask=mask, region=region)

    x_ds = x_ds.rename({'precip': f'{x_source}_precip'})
    y_ds = y_ds.rename({'precip': f'{y_source}_precip'})

    # get temperature from ERA5
    tmp_ds = era5(start_time, end_time, 'tmp2m', agg_days=agg_days, grid=grid, mask=mask, region=region)
    # get humidity from ERA5
    rh_ds = era5(start_time, end_time, 'rh2m', agg_days=agg_days, grid=grid, mask=mask, region=region)
    # get space_grouping labels
    agzones = space_grouping_labels(grid=grid, space_grouping=['agroecological_zone', 'admin_1'])
    # clip agzones to the region
    agzones = clip_region(agzones, grid=grid, region=region)
    import pdb; pdb.set_trace()
    ds = xr.merge([x_ds, y_ds, tmp_ds, agzones])

    # filter to time points in the month, if a month is provided
    #if month is not None:
    #    ds = ds.sel(time=ds.time.dt.month == month)

    # stack into a table
    ds = ds.stack(points=("time", "lat", "lon"))
    ds = ds.dropna("points")
    import pdb; pdb.set_trace()

    return ds

if __name__ == "__main__":
    start_remote(remote_name="precip_scatters")
    start_time = "2000-01-01"
    end_time = "2025-12-31"
    month = 4 # april

    grid = 'global0_25'
    mask = 'lsm'
    region = 'ghana'
    x_source = "imerg"
    y_source = "tahmo_avg"
    ds = pairwise_precip(start_time, end_time, x_source, y_source, agg_days=10, grid=grid, mask=mask, region=region)
    import pdb; pdb.set_trace()
    
    # scatter plot
    # convert to numpy array
    satellite = ds['imerg_precip'].values
    station = ds['tahmo_avg_precip'].values
    temperature = ds['tmp2m'].values
    data = np.vstack([satellite, station])
    # call kde to get density
    # z = gaussian_kde(data)(data)
    fig, ax = plt.subplots()
    ax.scatter(station, satellite, c=temperature, s=100, alpha=0.5)
    ax.set_xlabel('Station Precipitation (mm)')
    ax.set_ylabel('Satellite Precipitation (mm)')
    ax.set_title(f'{region} {start_time} to {end_time} {x_source} vs {y_source}')

    # get R^2
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(station, satellite)
    ax.text(0.05, 0.95, f"R^2: {r_value**2:.2f}", transform=ax.transAxes, fontsize=12, verticalalignment='top')

    plt.show()
    import pdb; pdb.set_trace()