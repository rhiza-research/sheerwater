import matplotlib.pyplot as plt
import os
from sheerwater.metrics import metric
from sheerwater.utils import start_remote
from sheerwater.spatial_subdivisions import get_spatial_subdivision_level, polygon_subdivision_geodataframe

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='gen2')
    # start_time = '2022-01-01'
    # end_time = '2022-12-31'
    start_time = "2014-01-01"
    end_time = "2024-12-31"

    variable = 'precip'
    # grid = 'global0_1'
    grid = 'global0_25'
    # grid = 'global1_5'
    mask = 'lsm'
    region = 'western_africa'
    # region = 'kenya'
    forecast = 'imerg_final'
    truth = 'tahmo_avg'
    # truth = 'chirps_v3'
    # fcst_threshold = 4.0
    # obs_threshold = 5.0
    # fcst_threshold = 1.0
    # obs_threshold = 0.5
    # agg_days = 7
    # above_days = 1
    # event = 'above_threshold'
    # event = 'days_above_threshold'
    # event = 'count_days_above_threshold'
    event = None
    # event = 'continuous_days_above_threshold'
    # event = 'nimbus_start_of_season_not_dry'
    # event = 'wet_spell'
    # event = 'nimbus_start_of_season'
    # event = 'start_of_season_by_accumulation'
    if event == 'days_above_threshold':
        # fcst_event_kwargs = {'agg_days': 30, 'threshold': 1.0, 'above_days': 3}
        # obs_event_kwargs = {'agg_days': 30, 'threshold': 0.5, 'above_days': 3}
        fcst_event_kwargs = {'agg_days': 21, 'threshold': 4.0, 'above_days': 6}
        obs_event_kwargs = {'agg_days': 21, 'threshold': 4.0, 'above_days': 6}
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
    else:
        fcst_event_kwargs = {}
        obs_event_kwargs = {}

    soft_margin = 182.5 # the full year
    detect_in_time = True
    if detect_in_time:
        metric_kwargs = {'soft_margin_in_days': soft_margin,
                         #  'detect_in_time': {'detect': 'first', 'time_grouping': 'two_seasons'}}
                         'detect_in_time': {'detect': 'change_point', 'time_grouping': 'year'}}
    else:
        metric_kwargs = {'soft_margin_in_days': soft_margin}

    data = []
    # for mn in ['pod', 'far']:
    # metrics = ['pod', 'far']
    metrics = ['pod']
    for mn in metrics:
        data.append(
            metric(start_time, end_time, variable='precip',
                   forecast=forecast, truth=truth,
                   metric_name=mn,
                   metric_kwargs=metric_kwargs,
                   event=event,
                   fcst_event_kwargs=fcst_event_kwargs,
                   obs_event_kwargs=obs_event_kwargs,
                   spatial=True, grid=grid,
                   recompute=True,
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
        'accumulation_threshold': 'ath',
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

    # POD plot
    if 'pod' in metrics:
        data[0].pod.plot(x="lon", y="lat", vmin=0.0, vmax=1.0, cmap='rainbow_r',
                         add_labels=False, cbar_kwargs={'label': 'POD'}, ax=axs[0])
        if country_gdf is not None:
            country_gdf.plot(ax=axs[0], edgecolor='black', linewidth=0.5, facecolor='none')
        axs[0].set_xlabel('Longitude')
        axs[0].set_ylabel('Latitude')

    # FAR plot
    if 'far' in metrics:
        data[1].far.plot(
            x="lon", y="lat", vmin=0.0, vmax=0.5, cmap='rainbow', add_labels=False,
            cbar_kwargs={'label': 'FAR'}, ax=axs[1]
        )
        if country_gdf is not None:
            country_gdf.plot(ax=axs[1], edgecolor='black', linewidth=0.5, facecolor='none')
        axs[1].set_xlabel('Longitude')
        axs[1].set_ylabel('Latitude')

    def fmt_kwargs(ev_kwargs):
        return ", ".join(f"{k}={v}" for k, v in sorted(ev_kwargs.items()))

    suptitle = (
        f"POD / FAR  |  {forecast} vs {truth}  |  {region}  |  event: {event}\n"
        f"soft_margin={soft_margin}d  |  {start_time} to {end_time}\n"
        f"detect_in_time={metric_kwargs.get('detect_in_time', 'None')}\n"
        f"fcst: {fmt_kwargs(fcst_event_kwargs)}\n"
        f"obs:  {fmt_kwargs(obs_event_kwargs)}"
    )
    fig.suptitle(suptitle, fontsize=10)
    if 'pod' in metrics:
        axs[0].set_title('POD')
    if 'far' in metrics:
        axs[1].set_title('FAR')
    plt.tight_layout(rect=[0, 0, 1, 0.90])

    filename = (
        f"pod_far_{event}_{forecast}_vs_{truth}_sm{soft_margin}d_{'detect_in_time' if detect_in_time else ''}"
        f"_fcst{compact_kwargs(fcst_event_kwargs)}_obs{compact_kwargs(obs_event_kwargs)}.pdf"
    )
    out_path = os.path.join(plot_dir, filename)
    plt.savefig(out_path, format='pdf', bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"Saved spatial POD/FAR plot to: {out_path}")
