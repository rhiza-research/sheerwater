"""Determine amount of total seasonal rainfall that is accumulated at onset date"""
import get_onset as go
from sheerwater.interfaces import get_data
from sheerwater.utils import start_remote

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='onset_issues2')

    time_grouping = 'kenya_rainy_season '
    start_time = "2000-01-01"
    end_time = "2025-12-31"
    mask = "lsm"
    region = "kenya"
    grid = "global0_25"

    # get onset dates
    imerg_onset = go.get_sos_dates(datasource="imerg_final", event_name="chc",
    start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region)

    # get accumulations
    imerg_accum = get_data("imerg_final")(start_time=start_time, end_time=end_time, grid=grid, mask=mask, region=region,
            event="seasonal_accumulation", event_kwargs={"time_grouping": "kenya_rainy_season "})

    acc = imerg_accum.drop_vars("group").chunk({"time": 365})
    time_vals = acc.time.values
    t = imerg_onset.time
    def nearest_idx(t_pixel):
        return np.abs(time_vals - t_pixel).argmin()

    t_idx = xr.apply_ufunc(
        nearest_idx,
        t,
        vectorize=True,
        dask="parallelized",
        output_dtypes=[np.int32],
    )

    onset = acc.precip.isel(time=t_idx.compute())
    final = imerg_accum.precip.groupby(imerg_accum.group).last("time")
    pct = onset / final

    import pdb; pdb.set_trace()

    # plot average percentage accumulations at onset for MAM and OND seasons
    mam_groups = [g for g in imerg_onset.group.values if "MAM" in str(g)]
    ond_groups = [g for g in imerg_onset.group.values if "OND" in str(g)]

    # compute stats
    mam_mean = pct.sel(group=mam_groups).mean("group").compute()
    mam_std  = pct.sel(group=mam_groups).std("group").compute()
    mam_max  = pct.sel(group=mam_groups).max("group").compute()

    ond_mean = pct.sel(group=ond_groups).mean("group").compute()
    ond_std  = pct.sel(group=ond_groups).std("group").compute()
    ond_max  = pct.sel(group=ond_groups).max("group").compute()

    # plot
    fig, axs = plt.subplots(3, 2, figsize=(10, 12))

    cmap = "turbo"
    vmin = 0
    vmax = 0.5

    # MAM column
    mam_mean.plot(ax=axs[0, 0], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)
    mam_std.plot(ax=axs[1, 0], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)
    mam_max.plot(ax=axs[2, 0], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)

    # OND column
    ond_mean.plot(ax=axs[0, 1], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)
    ond_std.plot(ax=axs[1, 1], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)
    im = ond_max.plot(ax=axs[2, 1], x="lon", vmin=vmin, vmax=vmax, cmap=cmap, add_colorbar=False)

    # create shared colorbar
    cbar = fig.colorbar(im, ax=axs, orientation="vertical", shrink=0.5, pad=0.02)
    cbar.set_label('Percentage of total accumulation at onset')
    cbar.set_ticks(np.arange(vmin, vmax, 0.1))

    # turn off all axis labels
    for ax in axs.flatten():
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title('')

    # titles
    axs[0, 0].set_title("MAM")
    axs[0, 1].set_title("OND")

    axs[0, 0].set_ylabel("mean")
    axs[1, 0].set_ylabel("std")
    axs[2, 0].set_ylabel("max")

    plt.show()


    import pdb; pdb.set_trace()


    
    