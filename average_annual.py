# compute the annual average series for each lat/lon of a region
from sheerwater.utils import start_remote
from sheerwater.data import imerg
from sheerwater.utils.grouping_utils import groupby_time
from sheerwater.data import tahmo_avg
import xarray as xr
from sheerwater.climatology import station_satellite_climatology

if __name__ == "__main__":
    start_remote(remote_name = "mohini_annual")

    start_time = "2015-01-01"
    end_time = "2024-12-31"
    region = "africa"

    grid = "global0_25"

    first_year = 2015
    last_year = 2024
    both = station_satellite_climatology("2024-01-01", "2024-12-31", first_year, last_year, region, grid=grid,
    recompute=True)
    import pdb; pdb.set_trace()

    # get imerg data for the region
    imerg = imerg(start_time, end_time, grid=grid, region=region)
    imerg = groupby_time(imerg, time_grouping='day_of_year', agg_fn='mean')
    # get tahmo data for the region
    tahmo = tahmo_avg(start_time, end_time, grid=grid, region=region)
    tahmo = groupby_time(tahmo, time_grouping='day_of_year', agg_fn='mean')

    # align datasets (safe even if already aligned)
    imerg, tahmo = xr.align(imerg, tahmo, join="inner")
    # rename precip to imerg_precip, tahmo_precip
    imerg = imerg.rename({'precip': 'imerg_precip'})
    tahmo = tahmo.rename({'precip': 'tahmo_precip'})

    # mask: keep only where tahmo exists
    import pdb; pdb.set_trace()
    mask = tahmo.tahmo_precip.notnull()

    both = xr.Dataset({
        "imerg": imerg.imerg_precip.where(mask),
        "tahmo": tahmo.tahmo_precip
    })
    import pdb; pdb.set_trace()
    both = both.stack(location=("lat", "lon"))

    # keep locations with at least some tahmo data
    valid_locs = both.tahmo.notnull().any(dim="time")

    both = both.sel(location=valid_locs)

    
    import pdb; pdb.set_trace()

