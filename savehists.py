from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import paired_histogram
import numpy as np

if __name__ == "__main__":
    start_remote(remote_name = "thresholds")#remote_config=["xlarge_cluster", "large_node"])

    # times
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # data sources
    estimate = "imerg_final"
    truth = "stations"

    # event defintion
    agg_days = 1
    dry_threshold = 0.5

    # spatial specs
    grid = "global0_25"
    space_grouping = None
    region = "kenya"
    spatial = False

    # get joint histogram
    bins = np.arange(0, 20, 0.1)
    hist = paired_histogram(start_time, end_time, estimate, truth, agg_days, grid=grid,
                            space_grouping=space_grouping, time_grouping=None, region=region,
                            spatial=spatial, bins=bins, recompute=True, zero_bin=True)
    import pdb; pdb.set_trace()
    hist = hist.drop_vars(['number', 'spatial_ref'])
    # convert to dataframe
    df = hist.to_dataframe()
    # unstack the dataframe
    df = df.unstack(level="truth")
    df.columns = df.columns.droplevel(0)
    df.index = df.index.astype(float)
    df.columns = df.columns.astype(float)
    # round index columns to 1 decimal place
    df.index = df.index.round(1)
    df.columns = df.columns.round(1)
    # save to pkl
    df.to_pickle(f"histograms/{region}_{agg_days}_sample.pkl")