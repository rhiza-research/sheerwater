from sheerwater.utils import start_remote
from sheerwater.metrics import metric
from dashboard_data.station_paired_analysis import hist_df
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    start_remote(remote_name = "mohini")

    start_time = "2015-01-01"
    end_time = "2024-12-31"
    estimate = "imerg_final"
    truth = "tahmo_avg"
    agg_days = 5
    grid = "global0_25"
    region = "kenya"
    time_grouping = None

    histdf = hist_df(start_time, end_time, estimate, truth, agg_days, grid, 
    region=region, time_grouping=time_grouping, recompute=['hist_df', 'paired_histogram'])
    # plot joint histogram

    region_totals = histdf.groupby("region_id")["precip"].sum()
    top_region = region_totals.idxmax()

    df = histdf[histdf["region_id"] == top_region].copy()

    # 2. keep only needed columns
    df = df[["estimate", "truth", "precip"]]

    # 3. pivot to 2D grid (truth = x, estimate = y)
    pivot = df.pivot_table(
    index="estimate",
    columns="truth",
    values="precip",
    aggfunc="sum",
    fill_value=0
    )

    # 4. log scale
    Z = np.log10(pivot.values + 1)

    # 5. plot
    plt.figure(figsize=(6, 5))

    plt.imshow(
    Z,
    origin="lower",
    aspect="equal",
    extent=[
        pivot.columns.min(), pivot.columns.max(),
        pivot.index.min(), pivot.index.max()
    ],
    cmap="viridis"
    )


    import pdb; pdb.set_trace()

