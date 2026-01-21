from sheerwater.data.chirps import chirps_gridded
from sheerwater.utils import start_remote

def regrid_chirps(start_time, end_time, version=2, stations=True):
    """Regrid CHIRPS data to a new grid."""
    ds = chirps_gridded(start_time, end_time, "chirps", version=version, stations=stations, cache_mode='write', recompute=True)
    return ds

if __name__ == "__main__":
    start_remote(remote_config='xxlarge_cluster', remote_name='mohini_regrid_chirps')
    version = 3 #, 2, 2
    stations = False # True, False
    ds = chirps_gridded(start_time="1998-01-01", end_time="2000-01-01",
                        grid="chirps",
                        version=version, stations=stations,
                        recompute=True, cache_mode='write')
