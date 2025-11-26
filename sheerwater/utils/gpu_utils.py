"""GPU utility functions for accelerating xarray/dask computations with CuPy.

This module provides utilities for converting xarray Datasets and DataArrays
between NumPy (CPU) and CuPy (GPU) backends. GPU acceleration can significantly
speed up large array computations.

Usage:
    # Enable GPU for a dataset
    ds = to_gpu(ds)

    # ... perform computations ...

    # Convert back to CPU before saving/serializing
    ds = to_cpu(ds)

Requirements:
    Install GPU dependencies with: pip install sheerwater[gpu]
    This installs cupy-xarray and dask-cuda.
"""
import logging
import os
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Environment variable name for GPU mode
# Using env var allows state to be shared between client and Dask workers
GPU_ENABLED_ENV_VAR = "SHEERWATER_GPU_ENABLED"

# Track whether GPU is available (cached per-process)
_GPU_AVAILABLE = None


def is_gpu_available():
    """Check if GPU acceleration is available.

    Returns:
        bool: True if cupy-xarray is installed and CUDA is available.
    """
    global _GPU_AVAILABLE
    if _GPU_AVAILABLE is not None:
        return _GPU_AVAILABLE

    try:
        import cupy_xarray  # noqa: F401
        import cupy as cp
        # Try to get device count to verify CUDA is actually available
        cp.cuda.runtime.getDeviceCount()
        _GPU_AVAILABLE = True
        logger.info("GPU acceleration available via cupy-xarray")
    except ImportError:
        _GPU_AVAILABLE = False
        logger.debug("cupy-xarray not installed. Install with: pip install sheerwater[gpu]")
    except Exception as e:
        _GPU_AVAILABLE = False
        logger.debug(f"GPU not available: {e}")

    return _GPU_AVAILABLE


def to_gpu(data, force=False):
    """Convert xarray Dataset or DataArray to use CuPy (GPU) arrays.

    For dask-backed arrays, this sets up the conversion to happen lazily
    when the task graph is computed - each chunk will be moved to GPU.

    Args:
        data: xarray Dataset or DataArray to convert.
        force: If True, raise an error if GPU is not available.
            If False (default), return data unchanged if GPU unavailable.

    Returns:
        Dataset or DataArray with data converted to CuPy arrays.

    Raises:
        RuntimeError: If force=True and GPU is not available.

    Example:
        >>> ds = xr.open_dataset("data.nc", chunks={"time": 100})
        >>> ds = to_gpu(ds)  # Conversion happens lazily
        >>> result = ds.mean(dim="time").compute()  # Computed on GPU
    """
    if not is_gpu_available():
        if force:
            raise RuntimeError(
                "GPU acceleration requested but not available. "
                "Install with: pip install sheerwater[gpu]"
            )
        logger.debug("GPU not available, returning data unchanged")
        return data

    import cupy_xarray  # noqa: F401

    # Check if data is already on GPU
    if hasattr(data, 'cupy') and hasattr(data.cupy, 'is_cupy'):
        if data.cupy.is_cupy:
            logger.debug("Data is already on GPU")
            return data

    logger.debug("Converting data to GPU (CuPy)")
    return data.cupy.as_cupy()


def to_cpu(data):
    """Convert xarray Dataset or DataArray back to NumPy (CPU) arrays.

    This should be called before saving data to disk or passing to
    functions that don't support CuPy arrays.

    Args:
        data: xarray Dataset or DataArray to convert.

    Returns:
        Dataset or DataArray with data converted to NumPy arrays.

    Example:
        >>> ds = to_gpu(ds)
        >>> result = ds.mean(dim="time")
        >>> result = to_cpu(result)  # Convert back before saving
        >>> result.to_netcdf("output.nc")
    """
    if not is_gpu_available():
        # If GPU isn't available, data should already be on CPU
        return data

    # Check if data has the cupy accessor and is on GPU
    if hasattr(data, 'cupy') and hasattr(data.cupy, 'is_cupy'):
        if data.cupy.is_cupy:
            logger.debug("Converting data from GPU to CPU (NumPy)")
            return data.cupy.as_numpy()

    # Data is already on CPU
    return data


def gpu_context(use_gpu=False):
    """Context manager for GPU-accelerated computation.

    This is a convenience wrapper that converts data to GPU on entry
    and ensures conversion back to CPU on exit.

    Args:
        use_gpu: Whether to enable GPU acceleration.

    Yields:
        tuple: (to_gpu_fn, to_cpu_fn) - Functions to convert data.

    Example:
        >>> with gpu_context(use_gpu=True) as (to_gpu, to_cpu):
        ...     ds = to_gpu(ds)
        ...     result = heavy_computation(ds)
        ...     result = to_cpu(result)
    """
    if use_gpu and is_gpu_available():
        yield to_gpu, to_cpu
    else:
        # No-op functions when GPU is disabled
        yield (lambda x: x), (lambda x: x)


def maybe_to_gpu(data, use_gpu=False):
    """Conditionally convert data to GPU based on flag.

    Args:
        data: xarray Dataset or DataArray.
        use_gpu: Whether to convert to GPU.

    Returns:
        Data, possibly converted to GPU.
    """
    if use_gpu:
        return to_gpu(data)
    return data


def maybe_to_cpu(data, use_gpu=False):
    """Conditionally convert data to CPU based on flag.

    Args:
        data: xarray Dataset or DataArray.
        use_gpu: Whether data might be on GPU and needs conversion.

    Returns:
        Data, converted to CPU if it was on GPU.
    """
    if use_gpu:
        return to_cpu(data)
    return data


def enable_gpu(enabled=True):
    """Enable or disable GPU mode globally.

    When GPU mode is enabled, `auto_gpu()` and `auto_cpu()` will
    automatically convert data to/from GPU.

    This sets an environment variable so the setting is visible to
    Dask workers (when using Coiled with environ propagation).

    Args:
        enabled: Whether to enable GPU mode.

    Returns:
        bool: Whether GPU is actually enabled (False if GPU not available).

    Example:
        >>> from sheerwater.utils import enable_gpu, auto_gpu, auto_cpu
        >>> enable_gpu(True)  # Enable GPU mode for this session
        >>> ds = auto_gpu(ds)  # Converts to GPU if enabled
        >>> result = ds.mean(dim="time")
        >>> result = auto_cpu(result)  # Converts back to CPU
    """
    if enabled:
        os.environ[GPU_ENABLED_ENV_VAR] = "1"
        logger.info("GPU mode enabled (set %s=1)", GPU_ENABLED_ENV_VAR)
    else:
        os.environ.pop(GPU_ENABLED_ENV_VAR, None)
        logger.info("GPU mode disabled")
    return is_gpu_enabled()


def is_gpu_mode_requested():
    """Check if GPU mode is requested via environment variable.

    This only checks the env var, NOT whether GPU is actually available.
    Use this to determine if we should attempt GPU operations (which may
    be lazy and execute on workers with GPUs).

    Returns:
        bool: True if GPU mode is requested.
    """
    return os.environ.get(GPU_ENABLED_ENV_VAR, "").lower() in ("1", "true", "yes")


def is_gpu_enabled():
    """Check if GPU mode is currently enabled AND GPU is available.

    Checks the environment variable and whether GPU is actually available.
    This works across client and Dask workers when the env var is propagated.

    Returns:
        bool: True if GPU mode is enabled and GPU is available.
    """
    if is_gpu_mode_requested() and is_gpu_available():
        return True
    return False


def auto_gpu(data):
    """Convert data to GPU if GPU mode is enabled.

    This uses the global GPU enabled flag set by `enable_gpu()`.

    For dask-backed arrays, this sets up lazy GPU conversion that happens
    on workers during compute(). This allows calling auto_gpu() on the client
    (which may not have GPU) and having the conversion happen on GPU workers.

    Args:
        data: xarray Dataset or DataArray.

    Returns:
        Data, converted to GPU if GPU mode is enabled.
    """
    if not is_gpu_mode_requested():
        return data

    # Try to convert to GPU - this will work on workers with cupy-xarray
    if is_gpu_available():
        return to_gpu(data)

    # If GPU not available locally but mode is requested, log a warning
    # This is expected on macOS clients - GPU conversion will happen on workers
    logger.debug("GPU mode requested but GPU not available locally (expected on macOS)")
    return data


def auto_cpu(data):
    """Convert data to CPU if GPU mode is enabled.

    This uses the global GPU enabled flag set by `enable_gpu()`.

    Args:
        data: xarray Dataset or DataArray.

    Returns:
        Data, converted to CPU if it was on GPU.
    """
    if is_gpu_enabled():
        return to_cpu(data)
    return data


@contextmanager
def benchmark(name="computation", verbose=True):
    """Context manager for benchmarking computation time.

    Args:
        name: Name to identify this benchmark.
        verbose: Whether to print timing info.

    Yields:
        dict: A dictionary that will contain timing results after the block.

    Example:
        >>> with benchmark("GPU metric computation") as timing:
        ...     result = ds.mean(dim="time").compute()
        >>> print(f"Took {timing['elapsed']:.2f}s")
    """
    results = {"name": name, "gpu_enabled": is_gpu_enabled()}
    start = time.perf_counter()

    try:
        yield results
    finally:
        elapsed = time.perf_counter() - start
        results["elapsed"] = elapsed
        if verbose:
            mode = "GPU" if results["gpu_enabled"] else "CPU"
            logger.info(f"[{mode}] {name}: {elapsed:.2f}s")
            print(f"[{mode}] {name}: {elapsed:.2f}s")


def benchmark_comparison(func, *args, warmup=1, runs=3, **kwargs):
    """Run a function with and without GPU to compare performance.

    Args:
        func: Function to benchmark (should accept *args and **kwargs).
        *args: Positional arguments to pass to func.
        warmup: Number of warmup runs (not timed).
        runs: Number of timed runs.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        dict: Comparison results with CPU and GPU timings.

    Example:
        >>> def compute_metric(ds):
        ...     return ds.mean(dim="time").compute()
        >>> results = benchmark_comparison(compute_metric, my_dataset)
        >>> print(f"Speedup: {results['speedup']:.2f}x")
    """
    results = {"warmup": warmup, "runs": runs}

    # CPU benchmark
    enable_gpu(False)
    cpu_times = []

    for i in range(warmup):
        logger.debug(f"CPU warmup {i+1}/{warmup}")
        func(*args, **kwargs)

    for i in range(runs):
        start = time.perf_counter()
        func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        cpu_times.append(elapsed)
        logger.info(f"CPU run {i+1}/{runs}: {elapsed:.2f}s")

    results["cpu_times"] = cpu_times
    results["cpu_mean"] = sum(cpu_times) / len(cpu_times)
    results["cpu_min"] = min(cpu_times)

    # GPU benchmark (if available)
    if is_gpu_available():
        gpu_enabled = enable_gpu(True)
        if gpu_enabled:
            gpu_times = []

            for i in range(warmup):
                logger.debug(f"GPU warmup {i+1}/{warmup}")
                func(*args, **kwargs)

            for i in range(runs):
                start = time.perf_counter()
                func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                gpu_times.append(elapsed)
                logger.info(f"GPU run {i+1}/{runs}: {elapsed:.2f}s")

            results["gpu_times"] = gpu_times
            results["gpu_mean"] = sum(gpu_times) / len(gpu_times)
            results["gpu_min"] = min(gpu_times)
            results["speedup"] = results["cpu_mean"] / results["gpu_mean"]

            enable_gpu(False)  # Reset
        else:
            results["gpu_times"] = None
            results["gpu_mean"] = None
            results["speedup"] = None
    else:
        results["gpu_times"] = None
        results["gpu_mean"] = None
        results["speedup"] = None

    # Print summary
    print(f"\n=== Benchmark Results ===")
    print(f"CPU mean: {results['cpu_mean']:.2f}s (min: {results['cpu_min']:.2f}s)")
    if results["gpu_mean"]:
        print(f"GPU mean: {results['gpu_mean']:.2f}s (min: {results['gpu_min']:.2f}s)")
        print(f"Speedup: {results['speedup']:.2f}x")
    else:
        print("GPU: not available")

    return results


def get_dask_performance_report(filename="performance_report.html"):
    """Get the Dask performance_report context manager.

    This wraps dask.distributed.performance_report for convenience.

    Args:
        filename: Output HTML filename for the report.

    Returns:
        Context manager for performance reporting.

    Example:
        >>> with get_dask_performance_report("my_benchmark.html"):
        ...     result = expensive_computation()
        ...     result.compute()
    """
    try:
        from dask.distributed import performance_report
        return performance_report(filename=filename)
    except ImportError:
        logger.warning("dask.distributed not available, using no-op context manager")

        @contextmanager
        def noop():
            yield
        return noop()


def print_dask_dashboard_link():
    """Print the Dask dashboard URL if available.

    The dashboard provides real-time visualization of:
    - Task stream (what's running on each worker)
    - Worker memory and CPU usage
    - Task progress
    - Bandwidth metrics
    """
    try:
        from dask.distributed import get_client
        client = get_client()
        print(f"\nDask Dashboard: {client.dashboard_link}")
        print("Key panels to watch:")
        print("  - Task Stream: Look for gaps (idle) or long bars (slow tasks)")
        print("  - Workers: Memory and thread utilization")
        print("  - Progress: Which task types are slowest")
        return client.dashboard_link
    except (ImportError, ValueError) as e:
        print(f"Dashboard not available: {e}")
        return None


def get_gpu_status():
    """Get detailed GPU status information.

    Returns a dict with GPU availability info. Useful for debugging
    GPU setup on workers.

    Returns:
        dict: GPU status information.
    """
    import socket
    status = {
        "hostname": socket.gethostname(),
        "gpu_env_var": os.environ.get(GPU_ENABLED_ENV_VAR, "not set"),
        "gpu_mode_requested": is_gpu_mode_requested(),
        "gpu_available": False,
        "gpu_enabled": False,
        "cupy_installed": False,
        "cupy_xarray_installed": False,
        "cuda_device_count": 0,
        "cuda_device_name": None,
        "error": None,
    }

    try:
        import cupy as cp
        status["cupy_installed"] = True
        try:
            device_count = cp.cuda.runtime.getDeviceCount()
            status["cuda_device_count"] = device_count
            if device_count > 0:
                status["cuda_device_name"] = cp.cuda.Device(0).name
        except Exception as e:
            status["error"] = f"CUDA error: {e}"
    except ImportError as e:
        status["error"] = f"cupy import error: {e}"

    try:
        import cupy_xarray  # noqa: F401
        status["cupy_xarray_installed"] = True
    except ImportError:
        pass

    status["gpu_available"] = is_gpu_available()
    status["gpu_enabled"] = is_gpu_enabled()

    return status


def check_worker_gpu_status():
    """Check GPU status on all Dask workers.

    Runs get_gpu_status() on each worker and prints the results.
    Useful for debugging GPU setup issues with Coiled.
    """
    try:
        from dask.distributed import get_client
        client = get_client()
    except (ImportError, ValueError) as e:
        print(f"No Dask client available: {e}")
        return None

    print("\n" + "=" * 60)
    print("CHECKING GPU STATUS ON WORKERS")
    print("=" * 60)

    # Run on all workers
    futures = client.run(get_gpu_status)

    for worker, status in futures.items():
        print(f"\nWorker: {worker}")
        print(f"  Hostname: {status['hostname']}")
        print(f"  GPU env var ({GPU_ENABLED_ENV_VAR}): {status['gpu_env_var']}")
        print(f"  GPU mode requested: {status['gpu_mode_requested']}")
        print(f"  cupy installed: {status['cupy_installed']}")
        print(f"  cupy-xarray installed: {status['cupy_xarray_installed']}")
        print(f"  CUDA devices: {status['cuda_device_count']}")
        if status['cuda_device_name']:
            print(f"  GPU name: {status['cuda_device_name']}")
        print(f"  GPU available: {status['gpu_available']}")
        print(f"  GPU enabled: {status['gpu_enabled']}")
        if status['error']:
            print(f"  ERROR: {status['error']}")

    print("=" * 60 + "\n")
    return futures
