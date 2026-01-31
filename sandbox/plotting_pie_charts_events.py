import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr
from sheerwater.satellite_station_misses import precip_events_table
from sheerwater.spatial_subdivisions import polygon_subdivision_geodataframe
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster')
    # period of interest
    start_time = "2020-01-01"
    end_time = "2025-12-31"
    # ground truth is tahmo
    truth = "tahmo_avg"
    # spatial resolution and region
    grid = 'global0_25'
    region = "ghana"

    precip_threshold = 38
    days = 5
    satellite = "imerg"

    events_fn = precip_events_table(start_time, end_time, days, precip_threshold, satellite, truth,
                                    'false_negative', grid, region, backend='parquet')
    events_tn = precip_events_table(start_time, end_time, days, precip_threshold, satellite, truth,
                                    'true_negative', grid, region, backend='parquet')
    events_tp = precip_events_table(start_time, end_time, days, precip_threshold, satellite, truth,
                                    'true_positive', grid, region, backend='parquet')
    events_fp = precip_events_table(start_time, end_time, days, precip_threshold, satellite, truth,
                                    'false_positive', grid, region, backend='parquet')

    try:
        events_fn = events_fn.compute()
        events_tn = events_tn.compute()
        events_tp = events_tp.compute()
        events_fp = events_fp.compute()
    except Exception as e:
        print(f"Error computing events: {e}")
        pass

    events_fn['metric'] = 'false_negative'
    events_tp['metric'] = 'true_positive'
    events_tn['metric'] = 'true_negative'
    events_fp['metric'] = 'false_positive'
    events = pd.concat([events_fn, events_tp, events_tn, events_fp])

    # Histogram of temperature, one for each metric, with slightly transparent bins
    # plt.hist(events[events['metric'] == 'false_negative']['era5_tmp2m'], label='false_negative', alpha=0.6)
    # plt.hist(events[events['metric'] == 'true_positive']['era5_tmp2m'], label='true_positive', alpha=0.6)
    # plt.hist(events[events['metric'] == 'true_negative']['era5_tmp2m'], label='true_negative', alpha=0.6)
    # plt.legend()
    # plt.show()

    # Select April events
    events_april = events[events['time'].dt.month == 5]

    # Drop nan temperatures for clean binning
    events_april = events_april.dropna(subset=['era5_tmp2m'])

    # Bin edges: from min to max in 5 deg C steps, rounded
    temp_min = np.floor(events_april['era5_tmp2m'].min() / 5) * 5
    temp_max = np.ceil(events_april['era5_tmp2m'].max() / 5) * 5
    bins = np.arange(temp_min, temp_max + 5, 5)
    labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)]
    events_april['temp_bin'] = pd.cut(events_april['era5_tmp2m'], bins=bins, labels=labels, include_lowest=True)

    # Group by temperature bin and metric
    counts = events_april.groupby(['temp_bin', 'metric']).size().unstack(fill_value=0)

    # Add total count annotations to the top of the stacked bars later after plotting, so prep the totals here
    import pdb
    pdb.set_trace()
    total_counts_per_bin = counts.sum(axis=1)

    # Get the max total count for scaling the annotations
    max_total_count = total_counts_per_bin.max()

    # Create a dict to map each bin to its total count
    bin_to_total_count = total_counts_per_bin.to_dict()

    # Get ratio by column (metric proportions within each bin, but let's do ratio across metrics in each temp_bin)
    counts_ratio = counts.div(counts.sum(axis=1), axis=0)
    metric_colors = {
        'false_negative': 'red',
        'true_positive': 'green',
        'true_negative': 'blue',
        'false_positive': 'yellow'
    }
    fig, axs = plt.subplots(2, 1, figsize=(8, 10), sharex=True)

    # First subplot: stacked bar chart with proportions (same as 'ax' before)
    counts_ratio.plot(kind='bar', stacked=True, color=[metric_colors[m] for m in counts_ratio.columns], ax=axs[0])
    axs[0].set_ylabel('Proportion of Events')
    axs[0].set_title('April Event Metric Proportion by Temperature Bin')
    axs[0].legend(title='Metric')

    # Second subplot: absolute counts for each metric and bin
    counts.plot(kind='bar', stacked=True, color=[metric_colors.get(m, 'grey') for m in counts.columns], ax=axs[1])
    axs[1].set_ylabel('Count of Events')
    axs[1].set_xlabel('Temperature Bin (°C)')
    axs[1].set_title('April Event Counts by Temperature Bin')
    axs[1].legend(title='Metric')

    plt.tight_layout()
    plt.show()
    import pdb
    pdb.set_trace()

    plot_april_histogram = False
    if plot_april_histogram:    # Select time points in April
        # Histogram of temperature, one for each metric, with slightly transparent bins
        plt.hist(events_april[events_april['metric'] == 'false_negative']
                 ['era5_tmp2m'], label='false_negative', alpha=0.6)
        plt.hist(events_april[events_april['metric'] == 'true_positive']
                 ['era5_tmp2m'], label='true_positive', alpha=0.6)
        plt.hist(events_april[events_april['metric'] == 'true_negative']
                 ['era5_tmp2m'], label='true_negative', alpha=0.6)
        plt.legend()
        plt.show()

    # Sum over time
    april_totals = events_april.groupby(['lat', 'lon', 'metric']).agg(
        count=('metric', 'count'),
        avg_era5_tmp2m=('era5_tmp2m', 'mean'),
        avg_tahmo_precip=('tahmo_avg_precip', 'mean'),
        avg_imerg_precip=('imerg_precip', 'mean'),
        avg_counts=('counts', 'mean'),
    )

    gdf = polygon_subdivision_geodataframe(level='admin_1')
    gdf['country'] = gdf['region_name'].str.split('-').str[0]
    region_gdf = gdf[gdf['country'] == region]
    region_gdf = region_gdf.to_crs(epsg=4326)

    # Add april totals scatter plot as a 2 x 2 subplot (one for each metric)
    april_totals = april_totals.reset_index()

    # To size the pie charts by the number of station counts, create a lookup dict for counts
    # We use the average_counts column in april_totals as our 'counts', indexed by (lat, lon)
    # Note: will use min/max scaling for radius within a reasonable range

    # Create a dict keyed by (lat, lon): avg_counts
    counts_lookup = april_totals.set_index(['lat', 'lon'])['avg_counts'].to_dict()
    # Get min/max for scaling
    count_values = list(counts_lookup.values())
    min_count = min(count_values)
    max_count = max(count_values)
    min_radius = 0.07   # Smallest pie
    max_radius = 0.25   # Largest pie

    def get_radius_for_count(count):
        # Scale linearly, protect against division by zero
        if max_count == min_count:
            return (max_radius + min_radius) / 2.0
        else:
            return min_radius + (count - min_count) / (max_count - min_count) * (max_radius - min_radius)

    metrics = [['false_negative', 'true_negative'], ['false_positive', 'true_positive']]
    fig, axes = plt.subplots(1, 2, figsize=(12, 10), sharex=True, sharey=True)
    for ax, metrics in zip(axes.flatten(), metrics):
        # For each lat/lon location, plot a mini pie chart showing the ratio of each metric
        region_gdf.plot(ax=ax, color='gray')

        # Prepare data: pivot so that each location is a row, metrics are columns, values are counts
        pivoted = april_totals.pivot_table(
            index=['lat', 'lon'],
            columns='metric',
            values='count',
            fill_value=0
        ).reset_index()

        # We'll draw a pie at each lat/lon
        from matplotlib.patches import Wedge

        colors = [metric_colors[m] for m in metrics]
        # The radius will be set per-pie below using get_radius_for_count(count).

        for idx, row in pivoted.iterrows():
            x, y = row['lon'], row['lat']
            counts = [row[m] for m in metrics]
            total = sum(counts)
            if total == 0:
                continue
            fracs = [c / total for c in counts]
            theta1 = 0
            for frac, color in zip(fracs, colors):
                if frac == 0:
                    continue
                theta2 = theta1 + frac * 360
                radius_count = april_totals[(april_totals['lat'] == row['lat']) & (
                    april_totals['lon'] == row['lon'])]['avg_counts'].values[0]
                wedge = Wedge(
                    center=(x, y),
                    r=get_radius_for_count(radius_count),
                    theta1=theta1,
                    theta2=theta2,
                    facecolor=color,
                    edgecolor='k',
                    linewidth=0.5
                )
                ax.add_patch(wedge)
                theta1 = theta2
        ax.set_title("Pie Ratios")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Add a legend
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], marker='o', color='w', label=m.replace('_', ' ').title(),
                                  markerfacecolor=metric_colors[m], markersize=10)
                           for m in metrics]
        ax.legend(handles=legend_elements, loc='upper right', title='Metric')
    plt.tight_layout()
    plt.show()
    import pdb
    pdb.set_trace()
