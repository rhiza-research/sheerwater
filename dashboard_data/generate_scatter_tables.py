from sheerwater.precip_scatters import pairwise_precip
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote(remote_name="precip_scatters")
    start_time = "2012-01-01"
    end_time = "2025-12-31"

    grid = 'global0_25'
    mask = 'lsm'
    agg_day_vals = [1, 5, 10]
    regions = ['kenya', 'ghana']
    precip1s = ["imerg", "chirps"]
    precip2 = "tahmo_avg"

    total_tables = len(regions) * len(precip1s) * len(agg_day_vals)
    current_table = 0
    for region in regions:
        for precip1 in precip1s:
            for agg_day in agg_day_vals:
                current_table += 1
                print(f"Generating scatter table for {precip1} and {precip2} in {region} with {agg_day} day aggregation ({current_table}/{total_tables})")
                df = pairwise_precip(start_time, end_time, precip1, precip2, agg_days=agg_day, grid=grid, mask=mask, region=region, recompute=True, cache_mode='overwrite')