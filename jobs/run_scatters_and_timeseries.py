"""Run the data needed to drive the scatter plots and timeseries plots."""
import argparse
from datetime import datetime
from sheerwater.utils import start_remote

from dashboard_data.station_paired_analysis import data_at_stations, scatter_data


parser = argparse.ArgumentParser(description="Run scatters and timeseries processing.")
parser.add_argument('--run_timeseries', action='store_true', help='Run data_at_stations for timeseries plots.')
parser.add_argument('--run_scatters', action='store_true', help='Run scatter_data for scatter plots.')
parser.add_argument('--remote', action='store_true', help='Run on remote cluster')
parser.add_argument('--truth', type=str, default="chirp_v3,chirps_v3,imerg_late,imerg_final,rain_over_africa",
                    help='Truth datasets to include.')


args = parser.parse_args()

if args.remote:
    start_remote(remote_config=['xxlarge_cluster', 'xlarge_node'])

truths = args.truth.split(',')

now = datetime.now().strftime("%Y-%m-%d")

if args.run_timeseries:
    for truth in truths:
        for grid in ['global0_1', 'global0_25', 'global1_5']:
            ds = data_at_stations(start_time='2015-01-01', end_time=now, data=truth,
                                  station='tahmo', grid=grid, variable='precip', backend='sql')
    # SMAP and TAHMO data are on the source grid
    ds = data_at_stations(start_time='2015-01-01', end_time=now, data='smap_l3',
                          station='tahmo', grid='source', variable='soil_moisture',
                          backend='sql', recompute=True)

    # SMAP and TAHMO data are on the source grid
    ds = data_at_stations(start_time='2015-01-01', end_time=now, data='smap_l3',
                          station='tahmo', grid='source', variable='soil_moisture',
                          backend='sql', recompute=True)

    ds = data_at_stations(start_time='2015-01-01', end_time=now, data='tahmo_avg',
                          station='tahmo_avg', grid='source', variable='precip',
                          backend='sql', recompute=True)

if args.run_scatters:
    for grid in ['global0_1', 'global0_25', 'global1_5']:
        for region in ['ghana', 'kenya']:
            for agg_days in [1, 5, 10]:
                sources = [(truth, 'precip') for truth in truths]
                # sources = [('rain_over_africa', 'precip'),
                #            ('chirps_v3', 'precip'),
                #            ('imerg_final', 'precip'),
                #            ('tahmo_avg', 'precip')]
                if grid in ['global0_25', 'global1_5']:
                    # ERA5 is only available on global0_25 and global1_5
                    # For now, commented out, because we aren't using these and it slows things down
                    # sources.append(('era5', 'tmp2m'))
                    # sources.append(('era5', 'rh2m'))
                    pass

                ds2 = scatter_data(start_time='2015-01-01', end_time=now,
                                   sources=sources,
                                   agg_days=agg_days,
                                   grid=grid, mask='lsm', region=region, backend='sql')
