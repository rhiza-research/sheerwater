from sheerwater.data.chirps import chirps_gridded, chirps_raw
from sheerwater.data.chirps import chirps_v2, chirp_v3, chirp_v2
import matplotlib.pyplot as plt
from sheerwater.utils.space_utils import clip_region
from sheerwater.utils.region_utils import region_data
from sheerwater.utils import start_remote
from nuthatch import cache

def check_chirps_gridded(start_time, end_time):
    # query chirps on chirps grid
    grid = "global0_05"
    # get each of the chirps
    # try each of the chirps calls and catch the error if it fails
    fig, ax = plt.subplots(2, 2, figsize=(20, 20))
    try:
        c2 = chirps_gridded(start_time, end_time, grid=grid, version=2, stations=False, cache_mode="read_only_strict")
        if c2 is not None:
            c2.precip.isel(time=1).plot(ax=ax[0, 0])
    except Exception as e:
        print(e)
    try:
        cs2 = chirps_gridded(start_time, end_time, grid=grid, version=2, stations=True, cache_mode="read_only_strict")
        if cs2 is not None:
            cs2.precip.isel(time=1).plot(ax=ax[0, 1])
    except Exception as e:
        print(e)
    try:
        c3 = chirps_gridded(start_time, end_time, grid=grid, version=3, stations=False, cache_mode="read_only_strict")
        if c3 is not None:
            c3.precip.isel(time=1).plot(ax=ax[1, 0])
    except Exception as e:
        print(e)
    try:
        cs3 = chirps_gridded(start_time, end_time, grid=grid, version=3, stations=True, cache_mode="read_only_strict")
        if cs3 is not None:
            cs3.precip.isel(time=1).plot(ax=ax[1, 1])
    except Exception as e:
        print(e)

    plt.show()

def check_chirps_single(year, grid, version, stations):
    try:
        c3 = chirps_raw(year, grid=grid, version=version, stations=stations, cache_mode="read_only_strict")
        # remove values below 0 and replace with 23
        c3 = c3.where(c3.precip >= 0, 23)
        c3.precip.isel(time=1).plot()
        import pdb; pdb.set_trace()
        plt.show()
    except Exception as e:
        print(e)

def check_chirps_raw(year):
       # get each of the chirps
    # try each of the chirps calls and catch the error if it fails
    fig, ax = plt.subplots(2, 2, figsize=(20, 20))
    grid = "chirps"
    try:
        c2 = chirps_raw(year, grid=grid, version=2, stations=False, cache_mode="read_only_strict")
        if c2 is not None:
            c2.precip.isel(time=1).plot(ax=ax[0, 0])
    except Exception as e:
        print(e)
    try:
        cs2 = chirps_raw(year, grid=grid, version=2, stations=True, cache_mode="read_only_strict")
        if cs2 is not None:
            cs2.precip.isel(time=1).plot(ax=ax[0, 1])
    except Exception as e:
        print(e)
    try:
        c3 = chirps_raw(year, grid=grid, version=3, stations=False, cache_mode="read_only_strict")
        if c3 is not None:
            c3.precip.isel(time=1).plot(ax=ax[1, 0])
    except Exception as e:
        print(e)
    try:
        cs3 = chirps_raw(year, grid=grid, version=3, stations=True, cache_mode="read_only_strict")
        if cs3 is not None:
            cs3.precip.isel(time=1).plot(ax=ax[1, 1])
    except Exception as e:
        print(e)

    plt.show()

if __name__ == "__main__":
    start_remote()
    year = 2020
    check_chirps_gridded(f"{year}-01-01", f"{year}-12-31")
    #check_chirps_raw(2010)
    #check_chirps_single(2010, "chirps", 3, False)