from sheerwater.data.chirps import chirps_raw, chirps_gridded
from sheerwater.utils import start_remote

if __name__ == "__main__":
    version = 2 #, 2, 2
    stations = True # True, False

    start_remote(remote_config='large_cluster', remote_name='mohini_test_chirps')
    # recompute raw chirps for version 3, no stations
    ds = chirps_gridded(start_time="2000-01-01", end_time="2025-12-31", grid="global0_05", version=3, stations=False, recompute=True, mask="lsm")
    #ds = chirps_raw(year=2025, grid="chirps", version=3, stations=False, recompute=True)
    import pdb; pdb.set_trace()
    ds.precip.isel(time=1).plot()