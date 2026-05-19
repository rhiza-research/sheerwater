import matplotlib.pyplot as plt
import os
import hashlib
import numpy as np
from sheerwater.metrics import metric
from sheerwater.utils import start_remote
from sheerwater.spatial_subdivisions import get_spatial_subdivision_level, polygon_subdivision_geodataframe
import argparse

if __name__ == "__main__":
    # start_remote(remote_config='xlarge_cluster', remote_name='bigger2')

    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute", action="store_true", help="Recompute the metrics.")
    parser.add_argument("--remote_name", type=str, default=None, help="Remote name to use.")
    parser.add_argument("--normalize", action="store_true", help="Normalize the metrics.")
    parser.add_argument("--vmax", type=float, default=None, help="Maximum value for the metrics.")
    args = parser.parse_args()
    start_remote(remote_config='xlarge_cluster', remote_name=args.remote_name)
    # start_time = '2022-01-01'
    # end_time = '2022-12-31'
    start_time = "2014-01-01"
    # start_time = "2023-01-01"
    end_time = "2024-12-31"
    # end_time = "2023-12-31"

    variable = 'precip'
    # grid = 'global0_1'
    grid = 'global0_25'
    # grid = 'global1_5'
    mask = 'lsm'
    # region = 'eastern_africa'
    region = 'kenya'
    # region = 'togo'
    time_grouping = 'rainy_season'
    # time_grouping = 'rainy_season'
    # time_grouping = 'two_seasons'
    # region = 'africa'
    # region = 'kenya'
    forecast = 'imerg_final'
    # forecast = 'chirps_v3'
    # forecast = 'rain_over_africa'
    # truth = 'tahmo_avg'
    truth = 'tahmo_avg'
    # truth = 'chirps_v3'
    # truth = 'rain_over_africa'
    # truth = 'chirp_v3'
    # truth = 'imerg_late'
    # truth = 'imerg_late'
    # fcst_threshold = 4.0
    # obs_threshold = 5.0
    # fcst_threshold = 1.0
    # obs_threshold = 0.5
    # agg_days = 7
    # above_days = 1
    # event = 'above_threshold'
    # event = 'days_above_threshold'
    # event = 'count_days_above_threshold'
    # event = None
    # event = 'seasonal_accumulation'
    # event = 'continuous_days_above_threshold'
    # event = 'nimbus_start_of_season_not_dry'
    # event = 'wet_spell'
    event = 'planting_suitability'
    # event = 'start_of_season_by_accumulation'
    if event == 'days_above_threshold':
        # fcst_event_kwargs = {'agg_days': 30, 'threshold': 1.0, 'above_days': 3}
        # obs_event_kwargs = {'agg_days': 30, 'threshold': 0.5, 'above_days': 3}
        fcst_event_kwargs = {'agg_days': 21, 'threshold': 4.0, 'above_days': 6}
        obs_event_kwargs = {'agg_days': 21, 'threshold': 4.0, 'above_days': 6}
    elif event == 'planting_suitability':
        fcst_event_kwargs = {'wet_spell_agg_days': 10, 'wet_spell_threshold': 20.0,
                             'dry_spell_agg_days': 20, 'dry_spell_threshold': 25.0}
        obs_event_kwargs = {'wet_spell_agg_days': 10, 'wet_spell_threshold': 20.0,
                            'dry_spell_agg_days': 20, 'dry_spell_threshold': 25.0}
    elif event == 'count_days_above_threshold':
        fcst_event_kwargs = {'agg_days': 21, 'threshold': 4.0}
        obs_event_kwargs = {'agg_days': 21, 'threshold': 4.0}
    elif event == 'continuous_days_above_threshold':
        fcst_event_kwargs = {'smoothing': 7, 'threshold': 4.0, 'continuous_days': 21}
        obs_event_kwargs = {'smoothing': 7, 'threshold': 5.0, 'continuous_days': 21}
    elif event == 'above_threshold':
        fcst_event_kwargs = {'agg_days': 1, 'threshold': 1.0}
        obs_event_kwargs = {'agg_days': 1, 'threshold': 0.5}
    elif event == 'nimbus_start_of_season':
        fcst_event_kwargs = {'dry_spell_agg_days': 5, 'dry_spell_threshold': 1.0, 'dry_spell_count': 1,
                             'wet_spell_agg_days': 5, 'wet_spell_threshold': 4.0, 'wet_spell_count': 2}
        obs_event_kwargs = {'dry_spell_agg_days': 5, 'dry_spell_threshold': 0.5, 'dry_spell_count': 1,
                            'wet_spell_agg_days': 5, 'wet_spell_threshold': 5.0, 'wet_spell_count': 2}
    elif event == 'nimbus_start_of_season_not_dry':
        wet_spell_agg_days = 15
        wet_spell_count = 5
        dry_spell_agg_days = 10
        dry_spell_count = 1
        fcst_event_kwargs = {'threshold': 1.0,
                             'dry_spell_agg_days': dry_spell_agg_days, 'dry_spell_count': dry_spell_count,
                             'wet_spell_agg_days': wet_spell_agg_days, 'wet_spell_count': wet_spell_count}
        obs_event_kwargs = {'threshold': 1.0,
                            'dry_spell_agg_days': dry_spell_agg_days, 'dry_spell_count': dry_spell_count,
                            'wet_spell_agg_days': wet_spell_agg_days, 'wet_spell_count': wet_spell_count}
    elif event == 'planting_suitability_by_count':
        fcst_event_kwargs = {'wet_spell_agg_days': 5, 'wet_spell_threshold': 4.0, 'wet_spell_count': 3,
                             'not_dry_spell_agg_days': 10, 'not_dry_spell_threshold': 1.0, 'not_dry_spell_count': 2}
        obs_event_kwargs = {'wet_spell_agg_days': 5, 'wet_spell_threshold': 4.0, 'wet_spell_count': 3,
                            'not_dry_spell_agg_days': 10, 'not_dry_spell_threshold': 1.0, 'not_dry_spell_count': 2}
    elif event == 'start_of_season_by_accumulation':
        fcst_event_kwargs = {'accumulation_threshold': 5.0}
        obs_event_kwargs = {'accumulation_threshold': 5.0}
    elif event == 'seasonal_accumulation':
        fcst_event_kwargs = {'time_grouping': time_grouping, 'by_percent': True}
        obs_event_kwargs = {'time_grouping': time_grouping, 'by_percent': True}
    else:
        fcst_event_kwargs = {}
        obs_event_kwargs = {}

    filter_event = None
    # filter_event = 'start_of_season_by_accumulation'
    # filter_event_kwargs = {'agg_days': 7, 'threshold': 5.0}
    # filter_event_kwargs = {'accumulation_threshold': 200.0, 'time_grouping': time_grouping}
    # filter_event_kwargs = {'accumulation_threshold': 0.75,  'by_percent': True, 'time_grouping': time_grouping}
    # filter_event_kwargs = {'time_grouping': time_grouping}
    filter_event_kwargs = {}
    soft_margin = 365  # the full year
    detect_in_time = True
    if detect_in_time:
        # filter_event_kwargs.update({'detect_in_time': {'detect': 'first', 'time_grouping': time_grouping}})
        fcst_event_kwargs.update({'detect_in_time': {'detect': 'first', 'time_grouping': time_grouping}})
        obs_event_kwargs.update({'detect_in_time': {'detect': 'first', 'time_grouping': time_grouping}})
        # filter_event_kwargs.update({'detect_in_time': {'detect': 'last_time', 'time_grouping': time_grouping}})

    metric_kwargs = {
        'obs_filter': False, 'fcst_filter': False,
        'soft_margin_in_days': 28,
    }
    if args.normalize:
        normalize = filter_event_kwargs.get('accumulation_threshold', 1.0)
    else:
        normalize = 1.0

    data = []
    # for mn in ['pod', 'far']:
    # metrics = ['pod', 'far']
    metrics = ['pod']
    # metrics = ['mae']
    # metrics = []
    for mn in metrics:
        data.append(
            metric(start_time, end_time, variable='precip',
                   forecast=forecast, truth=truth,
                   metric_name=mn,
                   metric_kwargs=metric_kwargs,
                   metric_event=event,
                   metric_event_kwargs_fcst=fcst_event_kwargs,
                   metric_event_kwargs_obs=obs_event_kwargs,
                   filter_event=filter_event,
                   filter_event_kwargs=filter_event_kwargs,
                   spatial=True, grid=grid,
                   recompute=args.recompute,
                   region=region)
        )

    # Flat output folder; uniqueness comes from the filename below.
    plot_dir = os.path.join('sos_plots', 'metrics', region, 'pod_far_spatial')
    os.makedirs(plot_dir, exist_ok=True)

    # Compact key shortener used for the filename (full info goes in the figure title).
    _SHORT_KEYS = {
        'agg_days': 'ad', 'above_days': 'abd', 'threshold': 'thr',
        'dry_spell_agg_days': 'dsad', 'dry_spell_threshold': 'dst', 'dry_spell_count': 'dsc',
        'wet_spell_agg_days': 'wsad', 'wet_spell_threshold': 'wst', 'wet_spell_count': 'wsc',
        'accumulation_threshold': 'ath', 'start_time': 'st', 'end_time': 'et',
    }

    def compact_kwargs(ev_kwargs):
        if not ev_kwargs:
            return ""
        return "-".join(f"{_SHORT_KEYS.get(k, k)}{v}" for k, v in sorted(ev_kwargs.items()))

    fig, axs = plt.subplots(1, len(metrics), figsize=(6*len(metrics), 6))
    if len(metrics) == 1:
        axs = [axs]

    try:
        level = get_spatial_subdivision_level(region)[0]
        country_gdf = polygon_subdivision_geodataframe(level=level, merged=False)
        country_gdf = country_gdf[country_gdf['region_name'] == region]
    except Exception as e:
        print(f"Error getting country boundaries for region {region}: {e}")
        country_gdf = None

    import matplotlib as mpl

    # POD plot
    if len(metrics) >= 1:
        met = metrics[0]
        field = data[0][met]
        if met in ['pod', 'far']:
            # For pod, far: rainbow discrete bins (pod reversed so high=blue, low=red)
            bounds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            norm = mpl.colors.BoundaryNorm(bounds, ncolors=len(bounds)-1)
            cmap_name = 'rainbow_r' if met == 'pod' else 'rainbow'
            cmap = mpl.colormaps[cmap_name].resampled(len(bounds)-1)
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': met}, ax=axs[0],
                norm=norm
            )
        elif met in ['bias', 'mae']:
            if met == 'bias':
                field = field / normalize
                if args.vmax is not None:
                    max_abs = args.vmax
                elif normalize == 1:
                    max_abs = float(np.abs(field).max().values)
                else:
                    max_abs = 1.0
                bounds = np.linspace(-max_abs, max_abs, 21)
                norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds)-1)
                cmap = mpl.colors.ListedColormap(
                    mpl.colormaps['nipy_spectral'](np.linspace(0.0, 0.9, len(bounds)-1))
                )
                cbar_label = f"{met}"
            else:  # 'mae'
                field = field / normalize
                if args.vmax is not None:
                    vmax = args.vmax
                elif normalize == 1:
                    vmax = float(field.max().values)
                else:
                    vmax = 1.0
                bounds = np.linspace(0.0, vmax, 11)
                norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds)-1)
                cmap = mpl.colors.ListedColormap(
                    mpl.colormaps['nipy_spectral'](np.linspace(0.45, 0.9, len(bounds)-1))
                )
                cbar_label = f"{met}"
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': cbar_label}, ax=axs[0],
                norm=norm, extend='both',
            )
        else:
            # Default to rainbow discrete
            n_bins = 11
            field_min = float(field.min().values)
            field_max = float(args.vmax) if args.vmax is not None else float(field.max().values)
            bounds = np.linspace(field_min, field_max, n_bins)
            norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=n_bins-1)
            cmap = mpl.colormaps['rainbow'].resampled(n_bins-1)
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': met}, ax=axs[0],
                norm=norm
            )

        field.plot(**plot_kwargs)
        if country_gdf is not None:
            country_gdf.plot(ax=axs[0], edgecolor='black', linewidth=0.5, facecolor='none')
        axs[0].set_xlabel('Longitude')
        axs[0].set_ylabel('Latitude')

    # FAR plot
    if len(metrics) >= 2:
        met = metrics[1]
        field = data[1][met]
        if met in ['pod', 'far']:
            # For pod, far: rainbow discrete bins (narrowed for FAR; pod reversed so high=blue, low=red)
            bounds = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
            norm = mpl.colors.BoundaryNorm(bounds, ncolors=len(bounds)-1)
            cmap_name = 'rainbow_r' if met == 'pod' else 'rainbow'
            cmap = mpl.colormaps[cmap_name].resampled(len(bounds)-1)
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': met}, ax=axs[1],
                norm=norm
            )
        elif met in ['bias', 'mae']:
            if met == 'bias':
                field = field / normalize
                if args.vmax is not None:
                    max_abs = args.vmax
                elif normalize == 1:
                    max_abs = float(np.abs(field).max().values)
                else:
                    max_abs = 1.0
                bounds = np.linspace(-max_abs, max_abs, 21)
                norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds)-1)
                cmap = mpl.colors.ListedColormap(
                    mpl.colormaps['nipy_spectral'](np.linspace(0.0, 0.9, len(bounds)-1))
                )
                cbar_label = f"{met}"
            else:  # 'mae'
                field = field / normalize
                if args.vmax is not None:
                    vmax = args.vmax
                elif normalize == 1:
                    vmax = float(field.max().values)
                else:
                    vmax = 1.0
                bounds = np.linspace(0.0, vmax, 11)
                norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds)-1)
                cmap = mpl.colors.ListedColormap(
                    mpl.colormaps['nipy_spectral'](np.linspace(0.45, 0.9, len(bounds)-1))
                )
                cbar_label = f"{met}"
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': cbar_label}, ax=axs[1],
                norm=norm, extend='both',
            )
        else:
            n_bins = 11
            field_min = float(field.min().values)
            field_max = float(args.vmax) if args.vmax is not None else float(field.max().values)
            bounds = np.linspace(field_min, field_max, n_bins)
            norm = mpl.colors.BoundaryNorm(boundaries=bounds, ncolors=n_bins-1)
            cmap = mpl.colormaps['rainbow'].resampled(n_bins-1)
            plot_kwargs = dict(
                x="lon", y="lat", cmap=cmap,
                add_labels=False, cbar_kwargs={'label': met}, ax=axs[1],
                norm=norm
            )

        field.plot(**plot_kwargs)
        if country_gdf is not None:
            country_gdf.plot(ax=axs[1], edgecolor='black', linewidth=0.5, facecolor='none')
        axs[1].set_xlabel('Longitude')
        axs[1].set_ylabel('Latitude')

    def fmt_kwargs(ev_kwargs):
        return ", ".join(f"{k}={v}" for k, v in sorted(ev_kwargs.items()))

    metric_labels = " / ".join(metrics)
    suptitle = (
        f"{metric_labels}  |  {forecast} vs {truth}  |  {region}  |  event: {event}\n"
        f"soft_margin={soft_margin}d  |  {start_time} to {end_time}\n"
        f"filter kwargs: {', '.join(f'{k}={v}' for k, v in sorted(filter_event_kwargs.items()))}\n"
        f"fcst: {fmt_kwargs(fcst_event_kwargs)}\n"
        f"obs:  {fmt_kwargs(obs_event_kwargs)}"

    )
    fig.suptitle(suptitle, fontsize=10)
    if len(metrics) >= 1:
        axs[0].set_title(metrics[0])
    if len(metrics) >= 2:
        axs[1].set_title(metrics[1])
    plt.tight_layout(rect=[0, 0, 1, 0.90])

    # Construct the descriptive filename string (unhashed, for hashing)
    descriptive_filename = (
        f"pod_far_{event}_{start_time}_{end_time}_{forecast}_vs_{truth}_sm{soft_margin}d_{'detect_in_time' if detect_in_time else ''}"
        f"_filter{compact_kwargs(filter_event_kwargs)}"
        f"_fcst{compact_kwargs(fcst_event_kwargs)}_obs{compact_kwargs(obs_event_kwargs)}"
    )
    # Hash the filename string to create a unique, short filename
    hash_digest = hashlib.sha256(descriptive_filename.encode()).hexdigest()[:16]
    filename = f"plot_{hash_digest}.png"
    out_path = os.path.join(plot_dir, filename)
    # Use a higher DPI for better quality
    plt.savefig(out_path, format='png', bbox_inches='tight', dpi=600)
    plt.show()
    plt.close()
    print(f"Saved spatial {metric_labels} plot to: {out_path} (DPI=600)")
