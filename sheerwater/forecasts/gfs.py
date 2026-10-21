"""Interface for GFS forecasts."""
import logging
import os
import re
import tempfile
from datetime import datetime

import dask
import numpy as np
import requests
import xarray as xr
from nuthatch import cache
from nuthatch.processors import timeseries

from sheerwater.utils import (
    dask_remote,
    densify_fcst,
    get_grid,
    get_variable,
    lon_base_change,
    regrid,
    shift_by_days,
)
from sheerwater.interfaces import forecast as sheerwater_forecast, spatial

logger = logging.getLogger(__name__)


@dask_remote
@timeseries(timeseries='init_time')
@spatial()
@cache(cache_args=['variable', 'grid', 'prob_type'],
       backend_kwargs={'chunking': {'lat': 121, 'lon': 240, 'lead_time': 35, 'time': 3, 'member': 30}},
       cache_disable_if={
           'grid': 'global0_25'
       })
def gfs_raw(start_time, end_time, variable='precip', prob_type='deterministic', grid='global1_5', # noqa: ARG001
            mask=None, region='global'):  # noqa: ARG001
    """Access GFS/GEFS raw."""
    # Fetched from earthmover directly into our bucket. Already meaned across members
    ds = xr.open_zarr('gs://sheerwater-datalake/gefs/gefs.zarr/')

    # Select the variable
    if variable != 'precip'  and variable != 'tmp2m':
        raise ValueError("Currently only supports precip and temp")

    ds = ds[[variable]]

    # If it's deterministic take the ensemble mean
    if prob_type != 'deterministic':
        raise ValueError("Currently only supports deterministic forecasts")

    _, _, size, _  = get_grid(grid)

    if size < 0.25:
        raise ValueError("GFS only supports grids of 0.25 or less.")

    if grid != 'global0_25':
        ds = regrid(ds, grid, base='base180', method='conservative', region=region)

    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'processors', 'processor_kwargs',
                   'lookback_source', 'densify', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 300, 'lon': 300, 'time': 10, 'lead_time': 35, 'member': 1}})
def gfs(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic', # noqa: ARG001
        event=None, event_kwargs=None,  # noqa: ARG001
        processors=None, processor_kwargs=None,  # noqa: ARG001
        lookback_source=None, densify=False,  # noqa: ARG001
        grid='global1_5', mask='lsm', region="global"):  # noqa: ARG001
    """Final GFS forecast interface."""
    # The earliest and latest forecast dates for the set of all leads
    forecast_start = shift_by_days(start_time, -35) if start_time is not None else None

    ds = gfs_raw(forecast_start, end_time, variable,
                 prob_type=prob_type, grid=grid, mask=mask,
                 region=region)

    # Reanme to standard naming
    ds = ds.rename({'lead_time': 'prediction_timedelta'})

    # Assign probability label
    ds = ds.assign_attrs(prob_type='deterministic')
    return ds


# ----------------------------------------------------------------------------------------------
# GEFSv12/CPC reforecast archive (hosted by UCSB CHC), a 20-year (1999-2018) hindcast used as a
# much longer-history alternative to `gfs`/`gefs_raw` (which only covers 2020-present). The
# archive is served as one raw NetCDF3 file per calendar day under
# https://data.chc.ucsb.edu/experimental/SubC/hindcasts/{pr,tas}/daily/EMC-GEFSv12_CPC/{month}/,
# but despite the "daily" naming the underlying forecasts are only initialized weekly
# (Wednesdays): each file is a redundant mirror carrying the 2 most recent weekly init dates
# (7 days apart) as of that file's nominal day, so most of the ~7000 files are exact duplicates
# of their neighbors. We sample one file every `_GEFS_CHC_SAMPLE_GAP_DAYS` days (safely under
# 14 days, i.e. 2 weekly steps -- any two files sampled that close together are guaranteed to
# cover overlapping or adjacent weeks) and rely on that redundancy plus a final drop-duplicates
# on init_time to reconstruct the full, non-redundant weekly init-time series without
# downloading every file.
_GEFS_CHC_DIR_URL = "https://data.chc.ucsb.edu/experimental/SubC/hindcasts/{var}/daily/EMC-GEFSv12_CPC/{month:02d}/"
_GEFS_CHC_SAMPLE_GAP_DAYS = 10


def _list_gefs_chc_files(var):
    """List (date_str, url) for every raw file in the archive for a given source variable name."""
    pattern = re.compile(rf'href="({var}_EMC-GEFSv12_CPC_(\d{{8}})\.daily\.nc)"')
    entries = {}
    for month in range(1, 13):
        dir_url = _GEFS_CHC_DIR_URL.format(var=var, month=month)
        resp = requests.get(dir_url, timeout=60)
        resp.raise_for_status()
        for fname, date_str in pattern.findall(resp.text):
            entries[date_str] = dir_url + fname
    return sorted(entries.items())


def _select_gefs_chc_sample_dates(dated_urls, gap_days=_GEFS_CHC_SAMPLE_GAP_DAYS):
    """Greedily pick dates at least `gap_days` apart from the available (date_str, url) pairs."""
    selected = []
    last_dt = None
    for date_str, url in dated_urls:
        dt = datetime.strptime(date_str, '%Y%m%d')
        if last_dt is None or (dt - last_dt).days >= gap_days:
            selected.append((date_str, url))
            last_dt = dt
    return selected


def _download_and_open_gefs_chc_file(url, max_attempts=3):
    """Download one archive file and open it, retrying on a truncated/corrupted download.

    Under heavy concurrent load (many workers hitting the CHC server at once for ~200MB files
    each), a connection can get reset or throttled mid-stream; `requests`' `iter_content()`
    doesn't raise just because the server closed early, so a truncated file can silently get
    written and fail to parse (netCDF4 raises an opaque low-level error for this, e.g. "Can't
    open HDF5 attribute", rather than something like a clear truncation error).
    """
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        with tempfile.NamedTemporaryFile(suffix='.nc') as tmp:
            with requests.get(url, stream=True, timeout=300) as resp:
                resp.raise_for_status()
                expected_size = resp.headers.get('content-length')
                for chunk in resp.iter_content(chunk_size=8 * 1024 * 1024):
                    tmp.write(chunk)
            tmp.flush()

            actual_size = os.path.getsize(tmp.name)
            if expected_size is not None and actual_size != int(expected_size):
                last_exc = ValueError(f"Truncated download of {url}: expected {expected_size} bytes, "
                                      f"got {actual_size}.")
            else:
                try:
                    return xr.open_dataset(tmp.name, decode_timedelta=True).load()
                except Exception as exc:  # noqa: BLE001 -- any parse failure means retry the download
                    last_exc = exc

        if attempt < max_attempts:
            logger.warning("gefs_chc_file: download of %s failed on attempt %d/%d (%s), retrying...",
                           url, attempt, max_attempts, last_exc)
    raise ValueError(f"Could not download/open {url} after {max_attempts} attempts.") from last_exc


@dask_remote
@cache(cache_args=['date_str', 'variable'],
       backend_kwargs={'chunking': {'lat': 24, 'lon': 24, 'S': -1, 'M': -1, 'L': -1}})
def gefs_chc_file(date_str, url, variable, grid='global1_0', mask=None, region='global'):  # noqa: ARG001
    """Fetches and processes a single raw GEFSv12/CPC reforecast archive file.

    No @spatial() -- clipping happens once at gefs_chc_raw; @spatial() breaks filepath_only=True
    (tries to clip a string). `url` is not a cache_arg (it's derived from `date_str`/`variable`
    by the caller and never varies independently of them). `grid` also isn't a cache_arg --
    the archive only has one native grid, so it's just a validated constant, not a real
    degree of freedom.

    lat/lon are tiled at the same 24x24 size `gefs_chc_raw` uses for its own combined cache
    (deliberately, not for this file's own chunk-size efficiency, since a single file's chunk
    would be tiny either way): if the per-file tiling doesn't match, combining ~750 of these
    into `gefs_chc_raw`'s small-tile/full-init_time layout requires a full spatial reshuffle
    (dask P2P shuffle) across the whole ~100GB+ combined dataset, which is exactly what timed
    out before this was aligned. With matching tiles, concatenating along init_time at combine
    time needs no cross-tile data movement at all.
    """
    if grid != 'global1_0':
        raise NotImplementedError("only supports the archive's native global1_0 grid.")

    var = get_variable(variable, 'gefs_chc')
    ds = _download_and_open_gefs_chc_file(url)

    ds = ds.rename({'S': 'init_time', 'M': 'member', 'L': 'prediction_timedelta', 'X': 'lon', 'Y': 'lat'})
    # Lead steps are centered on the day (offset 12h, e.g. "0 days 12:00:00") since they label a
    # daily accumulation/average window -- shift to whole-day leads so `init_time +
    # prediction_timedelta` lands on a clean calendar date, matching every other forecast source.
    ds = ds.assign_coords(prediction_timedelta=ds.prediction_timedelta - np.timedelta64(12, 'h'))
    ds = ds.rename_vars({var: variable})

    if variable == 'precip':
        ds[variable].attrs.update(units='mm / day')
    elif variable == 'tmp2m':
        # Raw archive is in Kelvin.
        ds[variable] = ds[variable] - 273.15
        ds[variable].attrs.update(units='C')

    ds[variable].encoding = {}
    ds = lon_base_change(ds, to_base="base180")
    ds = ds.sortby('lat')
    ds = ds.chunk({'lat': 24, 'lon': 24, 'init_time': -1, 'member': -1, 'prediction_timedelta': -1})
    return ds


@dask_remote
@spatial()
@cache(cache_args=['variable', 'grid'],
       backend_kwargs={'chunking': {'lat': 24, 'lon': 24, 'init_time': -1, 'member': 1,
                                    'prediction_timedelta': -1}})
def gefs_chc_raw(variable, grid='global1_0', mask=None, region='global'):
    """The full (1999-2018) GEFSv12/CPC weekly reforecast archive, deduplicated to unique init times.

    This is a fixed historical archive that will not grow, so (unlike a normal date-ranged
    fetch) it is cached once in full rather than incrementally by date range.

    Chunking keeps `init_time`/`prediction_timedelta` full (a per-cell climatology reduction
    needs the whole time axis together) but splits `member` into individual chunks -- with
    ~1000+ unique init_times, a full member x init_time x lead block would be several GB per
    lat/lon tile (member adds a factor of 11 that similar sources like `clim_stats_raw` don't
    have), so member is chunked separately and the lat/lon tile shrunk to compensate, targeting
    the usual ~100MB/chunk. This is safe because `.mean(dim='member')` (in `gefs_chc`) is a
    cheap, associative reduction dask handles fine across separate member chunks.
    """
    if grid != 'global1_0':
        raise NotImplementedError("only supports the archive's native global1_0 grid.")

    src_var = get_variable(variable, 'gefs_chc')
    dated_urls = _list_gefs_chc_files(src_var)
    sampled = _select_gefs_chc_sample_dates(dated_urls)
    logger.info("gefs_chc_raw: sampling %d of %d available archive files.", len(sampled), len(dated_urls))

    delayed_files = [dask.delayed(gefs_chc_file)(date_str, url, variable, grid=grid, mask=mask,
                                                 region=region, filepath_only=True, recompute=True,
                                                 cache_mode='overwrite')
                     for date_str, url in sampled]
    paths = dask.compute(*delayed_files)
    breakpoint()  # noqa: T100 -- inspect `paths` (all files fetched/cached) before combining.

    ds = xr.open_mfdataset(paths, engine='zarr', parallel=True, combine='nested', concat_dim='init_time')
    ds = ds.drop_duplicates('init_time').sortby('init_time')

    # Sanity check for gaps in the reconstructed weekly init-time series -- a gap larger than
    # two weeks means the underlying archive itself has a hole (not a sampling bug), since
    # consecutive sampled files always overlap by construction (see module docstring above).
    gaps = np.diff(ds.init_time.values) / np.timedelta64(1, 'D')
    if len(gaps) > 0 and gaps.max() > 14:
        logger.warning("gefs_chc_raw: found a %.0f-day gap in the reconstructed init_time series "
                       "-- the underlying archive appears to be missing data there.", gaps.max())

    ds[variable].encoding = {}
    ds = ds.chunk({'lat': 24, 'lon': 24, 'init_time': -1, 'member': 1, 'prediction_timedelta': -1})
    return ds


@dask_remote
@sheerwater_forecast()
@cache(cache=False,
       cache_args=['variable', 'agg_days', 'event', 'event_kwargs', 'processors', 'processor_kwargs',
                   'lookback_source', 'densify', 'prob_type', 'grid', 'mask', 'region'],
       backend_kwargs={'chunking': {'lat': 48, 'lon': 48, 'time': 10, 'prediction_timedelta': 35}})
def gefs_chc(start_time=None, end_time=None, variable="precip", agg_days=1, prob_type='deterministic',  # noqa: ARG001
            event=None, event_kwargs=None,  # noqa: ARG001
            processors=None, processor_kwargs=None,  # noqa: ARG001
            lookback_source=None,  # noqa: ARG001
            densify=False,
            grid='global1_0', mask='lsm', region="global"):
    """Final GEFSv12/CPC reforecast (hindcast) archive interface, 1999-2018.

    A much longer-history alternative to `gfs` (which is only 2020-present), at coarser
    resolution (1 degree) and weekly (not daily) initialization -- see `gefs_chc_raw`.

    Args:
        densify (bool): Whether to fill gaps between weekly reforecast issuance dates by
            repeating the nearest real forecast. Defaults to False (unlike
            `ecmwf_ifs_planette_reforecast`, another weekly/sparse-issuance source that
            defaults to True) since a common consumer of this function is a climatology
            (`clim_gefs_chc`) that needs the genuinely sparse series, not one padded with
            repeated values -- pass `densify=True` explicitly for a dense standalone forecast.
    """
    if variable not in ('precip', 'tmp2m'):
        raise ValueError("gefs_chc only supports precip and tmp2m.")
    if prob_type != 'deterministic':
        raise ValueError("gefs_chc currently only supports deterministic forecasts.")

    # Fetch a wider init_time window than requested (shifted back by the max lead), so that
    # inits from just before start_time -- whose long leads land inside [start_time, end_time]
    # -- are available to densify_fcst below. Without this, e.g. a real init 3 days before
    # start_time that would cover start_time+32 at lead=35 gets dropped before densify ever
    # sees it, leaving an unfillable gap at the front of the requested window (only the tail
    # end, past end_time, is expected to have real slop -- no init exists yet beyond end_time).
    forecast_start = shift_by_days(start_time, -35) if start_time is not None else None

    ds = gefs_chc_raw(variable, grid=grid, mask=mask, region=region)
    ds = ds.sel(init_time=slice(forecast_start, end_time))
    ds = ds.mean(dim='member', skipna=True)
    ds = ds.assign_attrs(prob_type='deterministic')

    if densify:
        attrs = ds.attrs
        # start_time/end_time here (not forecast_start) -- densify_fcst does its own final
        # init_time trim back down to the originally requested window.
        ds = densify_fcst(ds, start_time=start_time, end_time=end_time)
        ds = ds.assign_attrs(attrs)

    return ds
