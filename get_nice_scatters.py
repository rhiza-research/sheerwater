"""Generate a simple scatter plot comparing TAHMO and IMERG precipitation."""
from sheerwater.utils import start_remote
from dashboard_data.station_paired_analysis import scatter_data
import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_remote(remote_name="scatters")
    # get imerg at 0.25 and tahmo at 0.25 in kenya
    region = "kenya"
    grid = "global0_25"
    agg_days = 5
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    scats = scatter_data(
        start_time,
        end_time,
        grid=grid,
        region=region,
        agg_days=agg_days,
        source=[('tahmo_avg', 'precip'), ('imerg_late', 'precip')],
    )

    # use a nice matplotlib style - good for inclusion in papers
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10

    # plot a scatter, tahmo on x, imerg on y - color by lat, lon columns
    #colors = np.sqrt(scats["lat"].values**2 + scats["lon"].values**2)
    plt.scatter(scats['tahmo_avg_precip'], scats['imerg_final_precip'], alpha=0.3, c="green", cmap='rainbow')
    plt.xlabel("TAHMO Precipitation (mm / day)")
    plt.ylabel("IMERG Precipitation (mm / day)")
    plt.title(f"TAHMO vs IMERG Precipitation ({agg_days} day aggregation)")
    plt.show()
    #plt.savefig(f"tahmo_imerg_scatter_{agg_days}day.png")
