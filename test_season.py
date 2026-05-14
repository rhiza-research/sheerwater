from sheerwater.utils import start_remote
from sheerwater.data import tahmo_avg, imerg_late
from sheerwater.interfaces import get_data
from sheerwater.climatology import climatology

import xarray as xr
import numpy as np

def map_to_clim_rank(ds, clim):

    def _rank(x, clim_ts):

        # empirical percentile
        return (
            (clim_ts <= x).sum(dim="time")
            / clim_ts.count(dim="time")
        )

    return xr.apply_ufunc(
        _rank,
        ds,
        clim,
        input_core_dims=[[], ["time"]],
        output_core_dims=[[]],
        vectorize=True,
        dask="parallelized",
        output_dtypes=[float],
    )

if __name__ == "__main__":
    start_remote(remote_name="mohini")

    region = "ghana"
    grid = "global0_25"
    agg_days = 1
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    obs = "tahmo_avg"
    fcst = "imerg_late"

    obs_ds = get_data(obs)(start_time, end_time, grid=grid, region=region, agg_days=agg_days)
    fcst_ds = get_data(fcst)(start_time, end_time, grid=grid, region=region, agg_days=agg_days)

    # get climatology for each
    obs_clim = climatology("1996-01-01", "1996-12-31", "precip", first_year=2015, last_year=2024, agg_days=agg_days, data=obs, grid=grid, region=region)
    fcst_clim = climatology("1996-01-01", "1996-12-31", "precip", first_year=2000, last_year=2024, agg_days=agg_days, data=fcst, grid=grid, region=region)

    obs_rank = map_to_clim_rank(obs_ds, obs_clim)
    fcst_rank = map_to_clim_rank(fcst_ds, fcst_clim)

    import pdb; pdb.set_trace()





    



