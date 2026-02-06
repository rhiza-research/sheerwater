"""Generic earthaccess opener."""
import gcsfs
import xarray as xr
from dateutil import parser
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import dask_remote, regrid, roll_and_agg, get_grid_ds
from sheerwater.utils.secrets import earthaccess_password

from sheerwater.interfaces import data as sheerwater_data, spatial
import dask
import os
import earthaccess

@dask_remote
@cache(cache_args=['filename'])
def earthaccess_single_file(filename, earthaccess_result, preprocessor=None)

    KeyboardInterrupt
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    # Takes a single earthaccess result, fetches the file, opens it in xarray, the returns it to be cached
    earthaccess.download([earthaccess_result], local_path="./smap")

    ds = xr.open_datatree('./smap/' + filename, engine='h5netcdf', phony_dims='access')

    if preprocessor:
        ds = preprocessor(ds)

    ds = ds.compute()

    os.remove('./smap/' + filename)

    return ds


@dask_remote
def earthaccess_dataset(start_time, end_time, shortname, preprocessor=None, open_mfdataset_kwargs={}, delayed=False)
"""A generic interface to an earthaccess dataset.

    Opens data by shortname, and processes each file with the preprocessor before opening with mfdataset.

    NOT CACHED - make sure you cache the result!"""

    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    results = earthaccess.search_data(short_name=shortname, cloud_hosted=True, temporal=(start_time, end_time))

    if len(results) == 0:
        raise RuntimeError("No data found to open during that time.")

    files = []
    for result in results:
        fname = result.data_links()[0].split('/')[-1]
        if delayed:
            files.append(dask.delayed(earthaccess_single_file)(fname, result, preprocessor=preprocessor, filepath_only=True))
        else:
            files.append(earthaccess_single_file(fname, result, preprocessor=preprocessor, filepath_only=True))

    if delayed:
        files = dask.compute(*files)

    ds = xr.open_mfdataset(files,
                           engine='zarr',
                           parallel=True,
                           chunks={}
                           **open_mfdataset_kwargs))

    return ds
