from sheerwater.data.chirps import chirps_gridded
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt

def regrid_chirps(start_time, end_time, version=2, stations=True):
    """Regrid CHIRPS data to a new grid."""
    ds = chirps_gridded(start_time, end_time, "chirps", version=version, stations=stations, cache_mode='write', recompute=True)
    return ds

if __name__ == "__main__":
    start_remote(remote_config='xlarge_cluster', remote_name='mohini_regrid_chirps', region="us-west2")
    versions = [2, 2, 3]
    stations = [True, False, True]
    for i in range(len(versions)):
        version = versions[i]
        station = stations[i]
        ds = chirps_gridded(start_time="1998-01-01", end_time="2025-12-31",
                            grid="chirps",
                            version=version, stations=station,
                            recompute=True, cache_mode='overwrite')
