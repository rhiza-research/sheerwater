"""Generate Salient forecasts / reforecasts for all time."""
from itertools import product
from sheerwater_benchmarking.forecasts.abc import perpp_ecmwf


if __name__ == "__main__":
    vars = ["tmp2m", "precip"]
    # timescales = ["weeks34", "weeks56"]
    timescales = ["week1", "week2", "week3", "week4", "week5", "week6"]
    grids = ['global1_5']

    start_time = "2016-01-01"
    end_time = "2022-12-31"

    for var, lead, grid in product(vars, timescales, grids):
        try:
            ds = perpp_ecmwf(start_time, end_time, var, lead=lead, grid=grid,
                             remote=True,
                             remote_name='genevieve',
                             # recompute=True, force_overwrite=True
                             )
        except Exception as e:
            print(e)
