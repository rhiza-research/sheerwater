from sheerwater.data.chirps import chirps_raw
from sheerwater.utils import start_remote

if __name__ == "__main__":
    version = 2 #, 2, 2
    stations = True # True, False

    start_remote()
    # recompute raw chirps for version 3, no stations
    ds = chirps_raw(year=2025, grid="chirps", version=3, stations=False, recompute=True)
    import pdb; pdb.set_trace()
    ds.precip.isel(time=1).plot()