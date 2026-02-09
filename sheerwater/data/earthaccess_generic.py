"""Generic earthaccess opener."""
import xarray as xr
from nuthatch import cache

from sheerwater.utils.secrets import earthaccess_password
from sheerwater.utils import dask_remote

import dask
import os
import earthaccess

@dask_remote
@cache(cache_args=['filename', 'preprocessor_key'])
def earthaccess_single_file(filename, earthaccess_result, preprocessor=None, preprocessor_key=None): # noqa: ARG001
    """Download single earthaccess file."""
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    # Takes a single earthaccess result, fetches the file, opens it in xarray, the returns it to be cached
    earthaccess.download([earthaccess_result], local_path="./smap")

    ds = xr.open_datatree('./smap/' + filename, engine='h5netcdf', phony_dims='access')

    if preprocessor:
        ds = preprocessor(ds)

    if ds:
        ds = ds.compute()

    os.remove('./smap/' + filename)

    return ds


@dask_remote
def earthaccess_dataset(start_time, end_time, shortname, preprocessor=None, open_mfdataset_kwargs={},
                        delayed=False, limit=None):
    """A generic interface to an earthaccess dataset.

    Opens data by shortname, and processes each file with the preprocessor before opening with mfdataset.
    NOT CACHED - make sure you cache the result!
    """
    os.environ["EARTHDATA_USERNAME"] = "joshua_adkins"
    os.environ["EARTHDATA_PASSWORD"] = earthaccess_password()
    earthaccess.login(strategy="environment", persist=True)

    results = earthaccess.search_data(short_name=shortname, cloud_hosted=True, temporal=(start_time, end_time))
    results = results[:limit]

    if len(results) == 0:
        raise RuntimeError("No data found to open during that time.")

    if preprocessor:
        preprocessor_key = preprocessor.__name__
    else:
        preprocessor_key=None

    files = []
    for result in results:
        fname = result.data_links()[0].split('/')[-1]
        if delayed:
            files.append(dask.delayed(earthaccess_single_file)(fname, result, preprocessor=preprocessor,
                                                               preprocessor_key=preprocessor_key, filepath_only=True))
        else:
            files.append(earthaccess_single_file(fname, result, preprocessor=preprocessor,
                                                 preprocessor_key=preprocessor_key, filepath_only=True))

    if delayed:
        files = dask.compute(*files)

    files = [f for f in files if f is not None]

    ds = xr.open_mfdataset(files,
                           engine='zarr',
                           parallel=True,
                           chunks={},
                           **open_mfdataset_kwargs)

    return ds
