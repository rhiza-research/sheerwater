import argparse
import os
from sheerwater.utils import start_remote
from sheerwater.data import imerg, chirps_v3, rain_over_africa
from sheerwater.forecasts import ecmwf_ifs_er
from sheerwater.reanalysis import era5
from sheerwater.interfaces import get_data, get_forecast
from sheerwater.spatial_subdivisions import (
    polygon_subdivision_geodataframe,
    get_spatial_subdivision_level,
)
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm


def load_forecast(forecast, forecast_grid, truth, truth_grid, start_time, end_time, region,
                  agg_days, time_grouping, n_quantiles):
    """Raw + qqmap-debiased precip for a forecast/reanalysis source."""
    try:
        source = get_data(forecast)
    except:
        source = get_forecast(forecast)
    qqmap_kwargs = {
        'target': truth,
        'target_grid': truth_grid,
        'time_grouping': time_grouping,
        'n_quantiles': n_quantiles,
    }
    raw = source(start_time, end_time, variable='precip', grid=forecast_grid,
                 agg_days=agg_days, mask=None, region=region)
    debiased = source(start_time, end_time, variable='precip', grid=forecast_grid,
                      agg_days=agg_days, mask='lsm', region=region,
                      processors=['qqmap'], processor_kwargs=qqmap_kwargs)
    return raw, debiased


def load_truth(truth, grid, start_time, end_time, region, agg_days):
    return get_data(truth)(start_time, end_time, variable='precip', grid=grid,
                           agg_days=agg_days, mask='lsm', region=region)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downscaling/debias comparison plots.")
    parser.add_argument('--cluster', type=str, default='sheerwater_mudflat',
                        help='Cluster name for remote execution')
    args = parser.parse_args()
    start_remote(remote_name=args.cluster)

    start_time = '2015-01-01'
    end_time = '2025-12-31'
    # forecast = 'ecmwf_ifs_er'      # or 'era5'
    forecast = 'era5'      # or 'era5'
    truth = 'imerg'                # or 'era5', 'chirps_v3', ...
    coarse_grid = 'global0_25'      # forecast grid / coarse truth panel
    fine_grid = 'global0_1'        # qqmap target_grid / fine truth panel
    region = 'africa'
    agg_days = 7
    time_grouping = 'two_seasons_of_year'
    n_quantiles = 20

    times = [
        "2016-01-04", "2016-02-15", "2016-03-28", "2016-05-02", "2016-06-13",
        "2016-07-25", "2016-08-29", "2016-10-10", "2016-11-21", "2016-12-26",
    ]
    leads = [0, 7, 14, 21, 28, 35]   # positional indices into prediction_timedelta

    # --- load sources (shared path) ---
    raw, debiased = load_forecast(forecast, coarse_grid, truth, fine_grid, start_time, end_time,
                                  region, agg_days, time_grouping, n_quantiles)
    truth_fine = load_truth(truth, fine_grid, start_time, end_time, region, agg_days)    # panel 4
    truth_coarse = load_truth(truth, coarse_grid, start_time, end_time, region, agg_days)  # panel 1

    # Data has no lead dimension; ECMWF (forecast) does.
    has_lead = 'prediction_timedelta' in raw.dims
    lead_idx = leads if has_lead else [None]

    try:
        raw = raw.sel(time=times)
        debiased = debiased.sel(time=times)
        if has_lead:
            raw = raw.isel(prediction_timedelta=leads)
            debiased = debiased.isel(prediction_timedelta=leads)
    except:
        # Sometimes this fails - I'm not sure why? 
        import pdb; pdb.set_trace()
    raw = raw.compute()
    debiased = debiased.compute()
    truth_fine = truth_fine.sel(time=times).compute()
    truth_coarse = truth_coarse.sel(time=times).compute()

    # --- country boundaries ---
    level = get_spatial_subdivision_level(region)[0]
    if level == 'country':
        gdf = polygon_subdivision_geodataframe('admin_1')
        country_gdf = gdf[gdf['region_name'].str.contains(f"{region.lower()}-")]
    else:
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf['region_name'] == region]

    # --- colormap (weekly rainfall bounds) ---
    colors = ["#bdbdbd", "wheat", "lightgreen", "green",
              "lightblue", "blue", "yellow", "orange", "red", "purple"]
    cmap = LinearSegmentedColormap.from_list("wgbrp", colors)
    bounds = [0, 1.5, 3, 6, 9, 12, 16, 22, 29, 36, 50]
    norm = BoundaryNorm(bounds, cmap.N)

    # --- plotting (shared path) ---
    for ll, lead in enumerate(lead_idx):
        lead_tag = "all" if lead is None else lead
        output_dir = os.path.join(
            "downscaling_plots",
            f"{region}_{forecast}_vs_{truth}_lead{lead_tag}_agg{agg_days}_{time_grouping}_n{n_quantiles}",
        )
        os.makedirs(output_dir, exist_ok=True)
        for time in times:
            raw_field = raw.precip.sel(time=time)
            deb_field = debiased.precip.sel(time=time)
            if has_lead:
                raw_field = raw_field.isel(prediction_timedelta=ll)
                deb_field = deb_field.isel(prediction_timedelta=ll)

            fig, axes = plt.subplots(1, 4, figsize=(15, 4))
            truth_coarse.precip.sel(time=time).plot(x='lon', y='lat', cmap=cmap, norm=norm, ax=axes[0])
            raw_field.plot(x='lon', y='lat', cmap=cmap, norm=norm, ax=axes[1])
            deb_field.plot(x='lon', y='lat', cmap=cmap, norm=norm, ax=axes[2])
            truth_fine.precip.sel(time=time).plot(x='lon', y='lat', cmap=cmap, norm=norm, ax=axes[3])

            for ax in axes:
                country_gdf.plot(ax=ax, edgecolor='grey', linewidth=1.0, facecolor='none')

            axes[0].set_title(f"{truth} {coarse_grid}")
            axes[1].set_title("Raw")
            axes[2].set_title("QQMap")
            axes[3].set_title(f"{truth} {fine_grid}")
            fig.suptitle(
                f"{forecast} vs {truth} · agg_days={agg_days} · time={time} · lead={lead_tag} · "
                f"time_grouping={time_grouping} · n_quantiles={n_quantiles}"
            )
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            fname = (
                f"downscaling_region-{region}_forecast-{forecast}_truth-{truth}_lead-{lead_tag}_"
                f"agg-{agg_days}_timegroup-{time_grouping}_nq-{n_quantiles}_"
                f"time-{str(time).replace('-', '')}.png"
            )
            plt.savefig(os.path.join(output_dir, fname), dpi=200)
            plt.close(fig)
