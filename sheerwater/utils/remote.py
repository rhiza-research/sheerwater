"""Utilities for running functions on a remote dask cluster."""
from dask.distributed import Client, get_client, LocalCluster
import coiled
from coiled.credentials.google import send_application_default_credentials
import logging
from functools import wraps
import os
import pwd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config_options = {
    'large_scheduler': {
        'scheduler_vm_types': ['c2-standard-16', 'c3-standard-22']
    },
    'xlarge_scheduler': {
        'scheduler_vm_types': ['c2-standard-30', 'c3-standard-44']
    },
    'xxlarge_scheduler': {
        'scheduler_vm_types': ['c3-standard-88']
    },
    'on_demand': {
        'spot_policy': 'on-demand'
    },
    'single_cluster': {
        'n_workers': 1
    },
    'large_cluster': {
        'n_workers': [10, 11]
    },
    'xlarge_cluster': {
        'n_workers': [15, 16]
    },
    'xxlarge_cluster': {
        'n_workers': [25, 26]
    },
    'xxxlarge_cluster': {
        'n_workers': [35, 36]
    },
    'xc_cluster': {
        'n_workers': [70, 71]
    },
    'cc_cluster': {
        'n_workers': [200, 201]
    },
    'large_node': {
        'worker_vm_types': ['c2-standard-16', 'c3-standard-22']
    },
    'xlarge_node': {
        'worker_vm_types': ['c2-standard-30', 'c3-standard-44']
    },
    'xxlarge_node': {
        'worker_vm_types': ['c3-standard-88']
    },
    'xxxlarge_node': {
        'worker_vm_types': ['c3-standard-176']
    },
    'large_disk': {
        'worker_disk_size': '150GiB'
    },
    # GPU configurations - T4 GPUs (cheaper, good for testing)
    # T4 GPUs require N1 series VMs on GCP
    # scheduler_gpu required so CUDA packages can initialize on scheduler
    'gpu': {
        'worker_gpu': 1,
        'scheduler_gpu': 1,
        'worker_vm_types': ['n1-standard-4', 'n1-standard-8'],
        'scheduler_vm_types': ['n1-standard-4', 'n1-standard-8'],
    },
    'gpu_cluster': {
        'n_workers': [4, 8],
        'worker_gpu': 1,
        'scheduler_gpu': 1,
        'worker_vm_types': ['n1-standard-4', 'n1-standard-8'],
        'scheduler_vm_types': ['n1-standard-4', 'n1-standard-8'],
    },
    # A100 GPU configurations (high performance)
    # A100 GPUs use A2 instance family on GCP - GPUs are built into VM type
    # Explicitly set worker_gpu=0 and scheduler_gpu=0 to prevent Coiled from attaching
    # additional GPUs (it defaults to T4 otherwise, which fails on A2 VMs)
    # Region set to us-central1 which has good A100 availability
    'gpu_a100': {
        'worker_vm_types': ['a2-highgpu-1g'],  # 1x A100 40GB (built-in)
        'scheduler_vm_types': ['a2-highgpu-1g'],
        'worker_gpu': 0,
        'scheduler_gpu': 0,
        'region': 'us-central1',
    },
    'gpu_a100_large': {
        'worker_vm_types': ['a2-highgpu-2g'],  # 2x A100 40GB (built-in)
        'scheduler_vm_types': ['a2-highgpu-1g'],
        'worker_gpu': 0,
        'scheduler_gpu': 0,
        'region': 'us-central1',
    },
    'gpu_a100_cluster': {
        'n_workers': [2, 4],
        'worker_vm_types': ['a2-highgpu-1g'],  # 1x A100 40GB per worker (built-in)
        'scheduler_vm_types': ['a2-highgpu-1g'],
        'worker_gpu': 0,
        'scheduler_gpu': 0,
        'region': 'us-central1',
    },
    'gpu_a100_xlarge_cluster': {
        'n_workers': [4, 8],
        'worker_vm_types': ['a2-highgpu-2g'],  # 2x A100 40GB per worker (built-in)
        'scheduler_vm_types': ['a2-highgpu-1g'],
        'worker_gpu': 0,
        'scheduler_gpu': 0,
        'region': 'us-central1',
    },
}

# GPU conda packages to install via package_sync_conda_extras
# These are packages that require CUDA (not available on macOS) or system deps
_gpu_conda_packages = [
    'cupy',             # GPU arrays (requires CUDA, not available on macOS)
    'cupy-xarray',      # xarray integration for cupy
    'numba',            # Required by dask.distributed to serialize cupy arrays
    'geopandas',        # Spatial operations (install via conda to get GDAL)
    'pyogrio',          # Fast I/O for geopandas (needs GDAL from conda)
]



def start_remote(remote_name=None, remote_config=None):
    """Generic function to start a remote cluster."""
    from .gpu_utils import GPU_ENABLED_ENV_VAR

    default_name = 'sheerwater_' + pwd.getpwuid(os.getuid())[0]

    coiled_default_options = {
        'name': default_name,
        'n_workers': [3, 8],
        'idle_timeout': "120 minutes",
        'scheduler_vm_types': ['c2-standard-8', 'c3-standard-8'],
        'worker_vm_types': ['c2-standard-8', 'c3-standard-8'],
        'spot_policy': 'spot_with_fallback',
    }

    if remote_name and isinstance(remote_name, str):
        coiled_default_options['name'] = remote_name

    # Propagate GPU mode environment variable to workers if set
    gpu_mode = os.environ.get(GPU_ENABLED_ENV_VAR)
    if gpu_mode:
        # Determine GPU type suffix from remote_config for unique cluster names
        # This prevents Coiled from reusing clusters with different GPU types
        gpu_configs = ['gpu', 'gpu_cluster', 'gpu_a100', 'gpu_a100_large',
                       'gpu_a100_cluster', 'gpu_a100_xlarge_cluster']
        gpu_suffix = '_gpu'  # default
        if remote_config:
            config_list = remote_config if isinstance(remote_config, list) else [remote_config]
            for conf in config_list:
                if conf in gpu_configs:
                    gpu_suffix = f'_{conf}'
                    break
        coiled_default_options['name'] = coiled_default_options['name'] + gpu_suffix

        coiled_default_options['environ'] = {
            GPU_ENABLED_ENV_VAR: gpu_mode
        }
        logger.info("GPU mode enabled - propagating %s to workers", GPU_ENABLED_ENV_VAR)

        # Use package_sync with conda_extras to add GPU packages
        # This syncs local packages and adds GPU-specific conda packages that
        # aren't available locally (cupy requires CUDA, not available on macOS)
        coiled_default_options['package_sync'] = True
        coiled_default_options['package_sync_conda_extras'] = _gpu_conda_packages
        logger.info("Using package_sync with GPU conda extras: %s", _gpu_conda_packages)

    if remote_config and isinstance(remote_config, dict):
        # setup coiled cluster with remote config
        logger.info("Attaching to coiled cluster with custom configuration")
        coiled_default_options.update(remote_config)
    elif remote_config and (isinstance(remote_config, str) or
                            isinstance(remote_config, list)):
        logger.info("Attaching to coiled cluster with preset configuration")
        if not isinstance(remote_config, list):
            remote_config = [remote_config]

        for conf in remote_config:
            if conf in config_options:
                logger.info("Applying config '%s': %s", conf, config_options[conf])
                coiled_default_options.update(config_options[conf])
            else:
                print(f"Unknown preset remote config option {conf}. Skipping.")
    else:
        # Just setup a coiled cluster
        logger.info("Attaching to coiled cluster with default configuration")

    # Debug: show final cluster options
    logger.info("Final cluster options: %s", {k: v for k, v in coiled_default_options.items() if k != 'environ'})

    cluster = coiled.Cluster(**coiled_default_options)

    # send Application Default Credentials
    try:
        send_application_default_credentials(cluster)
    except Exception as e:
        print("Failed to send credentials", e)

    cluster.get_client()


def dask_remote(func):
    """Decorator to run a function on a remote dask cluster."""
    @wraps(func)
    def remote_wrapper(*args, **kwargs):
        # See if there are extra function args to run this remotely
        if 'remote' in kwargs and kwargs['remote']:

            remote_name = None
            if 'remote_name' in kwargs:
                remote_name = kwargs['remote_name']

            remote_config = None
            if 'remote_config' in kwargs:
                remote_config = kwargs['remote_config']

            start_remote(remote_name, remote_config)

        else:
            # Setup a local cluster
            try:
                get_client()
            except ValueError:
                logger.info("Starting local dask cluster...")
                cluster = LocalCluster(n_workers=2, threads_per_worker=2)
                Client(cluster)

        # call the function and return the result
        if 'remote' in kwargs:
            del kwargs['remote']

        if 'remote_config' in kwargs:
            del kwargs['remote_config']

        if 'remote_name' in kwargs:
            del kwargs['remote_name']

        return func(*args, **kwargs)
    return remote_wrapper
