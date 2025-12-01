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
    # A100 GPUs use A2 instance family on GCP
    'gpu_a100': {
        'worker_gpu': 1,
        'scheduler_gpu': 1,
        'worker_vm_types': ['a2-highgpu-1g'],  # 1x A100 40GB
        'scheduler_vm_types': ['a2-highgpu-1g'],
    },
    'gpu_a100_large': {
        'worker_gpu': 2,
        'scheduler_gpu': 1,
        'worker_vm_types': ['a2-highgpu-2g'],  # 2x A100 40GB
        'scheduler_vm_types': ['a2-highgpu-1g'],
    },
    'gpu_a100_cluster': {
        'n_workers': [2, 4],
        'worker_gpu': 1,
        'scheduler_gpu': 1,
        'worker_vm_types': ['a2-highgpu-1g'],  # 1x A100 40GB per worker
        'scheduler_vm_types': ['a2-highgpu-1g'],
    },
    'gpu_a100_xlarge_cluster': {
        'n_workers': [4, 8],
        'worker_gpu': 2,
        'scheduler_gpu': 1,
        'worker_vm_types': ['a2-highgpu-2g'],  # 2x A100 40GB per worker
        'scheduler_vm_types': ['a2-highgpu-1g'],
    },
}

# GPU packages to install on workers (cupy requires CUDA, not available on macOS)
# Also include geopandas/pyogrio from conda to avoid GDAL build issues
# numba is required for dask.distributed to serialize cupy arrays
_gpu_conda_packages = {
    'channels': ['conda-forge', 'rapidsai'],
    'dependencies': ['cupy', 'cupy-xarray', 'numba', 'geopandas', 'pyogrio', 'python=3.12'],
}


def _get_git_info():
    """Get git remote URL and current branch for the sheerwater package."""
    import subprocess
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    try:
        # Get remote URL
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True, text=True, cwd=repo_root
        )
        remote_url = result.stdout.strip() if result.returncode == 0 else None

        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, cwd=repo_root
        )
        branch = result.stdout.strip() if result.returncode == 0 else 'main'

        # Get commit hash for environment naming
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, cwd=repo_root
        )
        commit_hash = result.stdout.strip() if result.returncode == 0 else 'unknown'

        return remote_url, branch, commit_hash
    except Exception as e:
        logger.warning("Could not get git info: %s", e)
        return None, 'main', 'unknown'


def _ensure_gpu_software_env():
    """Ensure the GPU software environment exists with cupy packages and sheerwater from git."""
    remote_url, branch, _ = _get_git_info()

    env_name = "sheerwater-gpu"

    logger.info("Creating/checking GPU software environment: %s", env_name)

    # Build pip install URL for sheerwater from git
    pip_packages = []
    if remote_url:
        # Convert HTTPS URL to pip-installable format
        # e.g., https://github.com/org/repo.git -> git+https://github.com/org/repo.git@branch
        git_url = remote_url.replace('.git', '')
        pip_packages.append(f"sheerwater @ git+{git_url}.git@{branch}")
        logger.info("  Installing sheerwater from: git+%s.git@%s", git_url, branch)

    try:
        # Create environment with GPU conda packages and sheerwater from git
        coiled.create_software_environment(
            name=env_name,
            conda=_gpu_conda_packages,
            pip=pip_packages if pip_packages else None,
            gpu_enabled=True,
        )
        logger.info("GPU software environment ready: %s", env_name)
        return env_name
    except Exception as e:
        error_str = str(e).lower()
        if "already exists" in error_str or "exists" in error_str or "no changes" in error_str:
            logger.info("GPU software environment already exists: %s", env_name)
            return env_name
        logger.warning("Could not create GPU software environment: %s", e)
        return None


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
        # Use a separate cluster name for GPU mode to avoid conflicts
        coiled_default_options['name'] = coiled_default_options['name'] + '_gpu'

        coiled_default_options['environ'] = {
            GPU_ENABLED_ENV_VAR: gpu_mode
        }
        logger.info("GPU mode enabled - propagating %s to workers", GPU_ENABLED_ENV_VAR)

        # Ensure GPU software environment exists and use it
        # Note: Can't use both 'software' and 'package_sync' together
        gpu_env = _ensure_gpu_software_env()
        if gpu_env:
            coiled_default_options['software'] = gpu_env
            logger.info("Using GPU software environment: %s", gpu_env)
        else:
            # Fallback to package_sync if GPU env fails
            coiled_default_options['package_sync'] = True
            logger.warning("GPU env not available, using package_sync (no GPU packages)")

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
                coiled_default_options.update(config_options[conf])
            else:
                print(f"Unknown preset remote config option {conf}. Skipping.")
    else:
        # Just setup a coiled cluster
        logger.info("Attaching to coiled cluster with default configuration")

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
