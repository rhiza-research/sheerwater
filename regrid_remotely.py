from dask.distributed import Client
from sheerwater.data.chirps import chirps_gridded
import logging
import os
from sheerwater.utils import start_remote


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting CHIRPS regridding")

    # Attach to the cluster created by `coiled run`
    client = Client()

    version = 3 #, 2, 2
    stations = False # True, False

    start_remote(remote_config='xxlarge_cluster', remote_name='mohini_regrid_chirps')

    ds = chirps_gridded(start_time="1998-01-01", end_time="2020-12-31",
                        grid="chirps",
                        version=version, stations=stations,
                        recompute=True, cache_mode='overwrite')
    
    logging.info("Regridding complete")
