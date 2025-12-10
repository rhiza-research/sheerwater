import xarray as xr

from nuthatch.processor import NuthatchProcessor

from sheerwater.utils import clip_region

import logging
logger = logging.getLogger(__name__)


class spatial(NuthatchProcessor):
    """
    Processor for spatial data.

    This processor is used to slice a spatial dataset based on the region.

    It also validates the spatial data to ensure it has data within the region.

    It supports xarray datasets.
    """

    def __init__(self, region_dim=None, **kwargs):
        """
        Initialize the spatial processor.

        Args:
            region_dim: The name of the region dimension. If None, the returned dataset will not be 
                assumed to have a region dimesion and region data will be fetched from the region registry
                before clipping.
        """
        super().__init__(**kwargs)
        self.region_dim = region_dim

    def process_arguments(self, sig, *args, **kwargs):
        # Get default values for the function signature
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Get mask, region, and grid from bound args (includes defaults)
        try:
            self.region = bound_args.arguments.get('region')
            if self.region is None:
                raise ValueError(
                    "Region must be passed and be a default region.")
        except:
            raise ValueError(
                "Spatial functions must have the 'region' keyword argument")
        return args, kwargs

    def post_process(self, ds):
        if isinstance(ds, xr.Dataset):
            # Clip to specified region
            ds = clip_region(ds, region=self.region, region_dim=self.region_dim)
            # TODO: add support for pandas and dask dataframes?
            # elif isinstance(ds, pd.DataFrame) or isinstance(ds, dd.DataFrame):
        else:
            raise RuntimeError(f"Cannot clip by region for data type {type(ds)}")

        return ds

    def validate(self, ds):
        if isinstance(ds, xr.Dataset):
            # Check to see if the dataset extends roughly the full time series set
            test = clip_region(ds, region=self.region, region_dim=self.region_dim)
            if test.notnull().count().compute() == 0:
                print("""WARNING: The cached array does not have data within
                          the region {self.region}. Triggering recompute.
                          If you do not want to recompute the result set
                          `validate_data=False`""")
                return False
            else:
                return True
        else:
            raise RuntimeError(f"Cannot validate region for data type {type(ds)}")
