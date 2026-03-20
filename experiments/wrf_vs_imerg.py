from sheerwater.forecasts.kmd_wrf import kmd_wrf
from sheerwater.data.imerg import imerg_late
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
import numpy as np
from sheerwater.metrics import metric

# Same precip colormap as fetch_tahmo_data.py (grey at zero, then wheat→purple ramp).
_TAHMO_PRECIP_COLORS = [
    "#bdbdbd",
    "wheat",
    "lightgreen",
    "green",
    "lightblue",
    "blue",
    "yellow",
    "orange",
    "red",
    "purple",
]
TAHMO_PRECIP_CMAP = LinearSegmentedColormap.from_list("wgbrp", _TAHMO_PRECIP_COLORS)
TAHMO_PRECIP_BOUNDS = [x / 10 for x in [0, 10, 20, 40, 60, 80, 110, 150, 200, 250, 350]]
TAHMO_PRECIP_NORM = BoundaryNorm(TAHMO_PRECIP_BOUNDS, TAHMO_PRECIP_CMAP.N)
if __name__ == "__main__":
    # start_remote(remote_config='xlarge_cluster')
    start_time = '2025-09-19'
    end_time = '2025-09-25'
    eval_date = '2025-09-19'
    agg_days = 7
    variable = 'precip'
    ds = kmd_wrf(start_time, end_time, variable, grid='global0_1',
                 agg_days=agg_days, region='kenya', mask='lsm')
    ds = ds.sel(time=eval_date)
    ds_imerg = imerg_late(start_time, end_time, agg_days=agg_days, grid='global0_1', region='kenya', mask='lsm')
    ds_imerg = ds_imerg.sel(time=eval_date)

    # Plot in 3 subplots IMERG and KMD WRF
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    ds_imerg.precip.plot(
        x='lon',
        y='lat',
        label='mm /day',
        ax=axes[0],
        cmap=TAHMO_PRECIP_CMAP,
        norm=TAHMO_PRECIP_NORM,
    )
    ds.isel(prediction_timedelta=0).precip.plot(
        x='lon',
        y='lat',
        ax=axes[1],
        label='mm /day',
        cmap=TAHMO_PRECIP_CMAP,
        norm=TAHMO_PRECIP_NORM,
    )
    diff = ds_imerg.precip - ds.precip
    diff_slice = diff.isel(prediction_timedelta=0)
    vmax = float(np.nanmax(np.abs(diff_slice.values)))
    if not np.isfinite(vmax) or vmax == 0:
        vmax = 1.0
    diff_slice.plot(
        x='lon',
        y='lat',
        ax=axes[2],
        label='mm /day',
        cmap='RdBu_r',
        vmin=-vmax,
        vmax=vmax,
    )
    axes[0].set_title(f'IMERG')
    axes[1].set_title('KMD WRF')
    axes[2].set_title('Difference')
    # Set the colorbar label to mm /day
    # Set the overall title
    fig.suptitle(f'7 day accumulated precipitation from {start_time} to {end_time}')

    import pdb
    pdb.set_trace()
    val = metric(start_time, end_time, variable, agg_days=7, forecast='kmd_wrf',
                 truth='imerg_late', metric_name='heidke-1-5-10-20', grid='global0_1', region='kenya',
                 recompute=True)
    print(val)
    data = metric(start_time, end_time, variable, agg_days=7, forecast='kmd_wrf',
                  truth='imerg_late', metric_name='mae', grid='global0_1', region='kenya',
                  spatial=True, recompute=True)
    import pdb
    pdb.set_trace()
    plt.show()
    data.mae.plot(x='lon')
