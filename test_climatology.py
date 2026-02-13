# get era5 climatology for ghana
from sheerwater.climatology import climatology_2020
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()
    start_time = "2024-01-01"
    end_time = "2024-12-31"
    climatology = climatology_2020(start_time, end_time, variable='precip', agg_days=5, grid='global0_25', mask='lsm', region='ghana')
    import pdb; pdb.set_trace()