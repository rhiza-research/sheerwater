# compute the annual average series for each lat/lon of a region

from sheerwater.utils import start_remote
from sheerwater.climatology import station_satellite_climatology

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import math
import matplotlib.dates as mdates

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":

    start_remote(remote_name="mohini")

    start_time = "2015-01-01"
    end_time = "2024-12-31"
    region = "africa"
    grid = "global0_25"

    first_year = 2015
    last_year = 2024

    both = station_satellite_climatology(
        "2024-01-01",
        "2024-12-31",
        first_year,
        last_year,
        region,
        grid=grid
    )

    df = both.copy()

    # --------------------------------------------------
    # PREP
    # --------------------------------------------------
    df['time'] = pd.to_datetime(df['time'])
    df['point_id'] = list(zip(df['lat'], df['lon']))

    # --------------------------------------------------
    # PIVOT IMERG TIME SERIES
    # --------------------------------------------------
    imerg_ts = df.pivot_table(
        index='point_id',
        columns='time',
        values='imerg'
    ).sort_index(axis=1)

    # --------------------------------------------------
    # HANDLE MISSING VALUES
    # --------------------------------------------------
    imerg_ts = imerg_ts.fillna(0)

    # --------------------------------------------------
    # MIN-MAX NORMALIZATION (0–1 per location)
    # --------------------------------------------------
    X = imerg_ts.values.astype(float)

    row_min = np.nanmin(X, axis=1, keepdims=True)
    row_max = np.nanmax(X, axis=1, keepdims=True)

    denom = np.where((row_max - row_min) == 0, 1, row_max - row_min)

    X_scaled = (X - row_min) / denom

    # --------------------------------------------------
    # KMEANS
    # --------------------------------------------------
    k = 6
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # --------------------------------------------------
    # CENTROIDS (IMPORTANT: use scaled space!)
    # --------------------------------------------------
    centroids = kmeans.cluster_centers_

    # --------------------------------------------------
    # SPATIAL DATAFRAME
    # --------------------------------------------------
    coords = np.array(imerg_ts.index.tolist())

    cluster_df = pd.DataFrame({
        "lat": coords[:, 0],
        "lon": coords[:, 1],
        "cluster": labels
    })

    times = pd.to_datetime(imerg_ts.columns.values)
    unique_clusters = np.unique(labels)

    colors = plt.cm.tab10(np.linspace(0, 1, k))

    # ==================================================
    # FIGURE 1: TIME SERIES SMALL MULTIPLES
    # ==================================================
    n_cols = 3
    n_rows = math.ceil(k / n_cols)

    fig_ts = plt.figure(figsize=(18, 4 * n_rows))
    gs_ts = fig_ts.add_gridspec(n_rows, n_cols)

    for i, cluster_id in enumerate(unique_clusters):

        r = i // n_cols
        c = i % n_cols

        ax = fig_ts.add_subplot(gs_ts[r, c])

        members = X_scaled[labels == cluster_id]

        # -------------------------
        # members (very light)
        # -------------------------
        for m in members:
            ax.plot(
                times,
                m,
                color=colors[cluster_id],
                alpha=0.03,
                linewidth=0.8
            )

        # -------------------------
        # centroid (bold)
        # -------------------------
        ax.plot(
            times,
            centroids[cluster_id],
            color=colors[cluster_id],
            linewidth=2.5
        )

        # -------------------------
        # Y range (scaled space)
        # -------------------------
        ax.set_ylim(0, 1)

        # -------------------------
        # MONTH TICKS
        # -------------------------
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

        ax.set_title(f"Cluster {cluster_id}")

        # show labels only bottom row
        if r != n_rows - 1:
            ax.tick_params(axis='x', labelbottom=False)

        ax.set_yticks([])

    fig_ts.suptitle("IMERG Cluster Time Series", y=1.02)
    plt.tight_layout()
    plt.show()
    import pdb; pdb.set_trace()

    # ==================================================
    # FIGURE 2: SPATIAL MAP
    # ==================================================
    fig_map, ax_map = plt.subplots(figsize=(10, 6))

    scatter = ax_map.scatter(
        cluster_df["lon"],
        cluster_df["lat"],
        c=cluster_df["cluster"],
        cmap="tab10",
        s=12,
        alpha=0.85
    )

    ax_map.set_title("Spatial Distribution of IMERG Clusters")
    ax_map.set_xlabel("Longitude")
    ax_map.set_ylabel("Latitude")

    plt.colorbar(scatter, ax=ax_map, label="Cluster")

    plt.tight_layout()
    plt.show()