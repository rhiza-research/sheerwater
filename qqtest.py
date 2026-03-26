from sheerwater.utils import start_remote
from sheerwater.data import tahmo_avg, imerg_late
from sheerwater.utils.grouping_utils import groupby_time
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # get a "ranked" climatology of the source and target
    # let's do this for kenya. 

    # from tahmo, get day of year precip over grid cells. 
    # from imerg, get day of year precip over grid cells. 
    start_remote(remote_name="qqtest")

    region = "kenya"
    grid = "global0_25"
    agg_days = 10
    start_time = "2015-01-01"
    end_time = "2024-12-31"
    tahmo = tahmo_avg(start_time, end_time, grid=grid, region=region, agg_days=agg_days)
    imerg = imerg_late(start_time, end_time, grid=grid, region=region, agg_days=agg_days)
    rankon = "month_of_year" # day_of_year, year, all
    # add time group coolumn
    ranked_tahmo = groupby_time(tahmo.precip, rankon, agg_fn="rank")
    ranked_imerg = groupby_time(imerg.precip, rankon, agg_fn="rank")
    # for each time grouping, determine ranking

    # plot a map of rank vs precip for both sources in a 2x2 plot
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    tidx = 100
    import pdb; pdb.set_trace()
    axs[0, 0].imshow(ranked_tahmo.isel(time=tidx).values, cmap="viridis")
    axs[0, 1].imshow(ranked_imerg.isel(time=tidx).values, cmap="viridis")
    axs[1, 0].imshow(tahmo.precip.isel(time=tidx).values, cmap="viridis")
    axs[1, 1].imshow(imerg.precip.isel(time=tidx).values, cmap="viridis")
    import pdb; pdb.set_trace()
    plt.show()

