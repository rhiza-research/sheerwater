"""A decorator for spatial data."""
import xarray as xr

from nuthatch.processor import NuthatchProcessor

from sheerwater.spatial_subdivisions import clip_region, apply_mask
from .datasets import add_spatial_attrs, check_spatial_attr

import logging
logger = logging.getLogger(__name__)


class spatial(NuthatchProcessor):
    """Processor for spatial data.

    This processor is used to slice a spatial dataset based on the region.

    It also validates the spatial data to ensure it has data within the region.

    It supports xarray datasets.
    """

    def __init__(self, region_dim=None, **kwargs):
        """Initialize the spatial processor.

        Args:
            region_dim (str): The name of the region dimension. If None, the returned dataset will not be
                assumed to have a region dimesion and region data will be fetched from the region registry
                before clipping.
            kwargs: Additional keyword arguments to pass to the NuthatchProcessor.
        """
        super().__init__(**kwargs)
        self.region_dim = region_dim

    def process_arguments(self, sig, *args, **kwargs):
        """Process the arguments for the spatial decorator."""
        # Get default values for the function signature
        bound_args = self.bind_signature(sig, *args, **kwargs)

        # Default to global region and no masking if not passed
        self.region = bound_args.arguments.get('region', 'global')
        self.mask = bound_args.arguments.get('mask', None)
        try:
            self.grid = bound_args.arguments['grid']
        except KeyError:
            print("WARNING: No grid passed to spatial decorator. Cannot perform masking or region clipping.")
            self.mask = None
            self.grid = None
        return args, kwargs

    def post_process(self, ds):
        """Post-process the dataset to clip to the region and apply the mask."""
        if isinstance(ds, xr.Dataset):
            # Clip to specified region
            if not check_spatial_attr(ds, region=self.region):
                # Only clip region if the dataframe hasn't already been clipped
                ds = clip_region(ds, grid=self.grid, region=self.region, region_dim=self.region_dim)
            if not check_spatial_attr(ds, mask=self.mask):
                # Only apply mask if this dataframe has not already been masked
                ds = apply_mask(ds, self.mask, grid=self.grid)
            ds = add_spatial_attrs(ds, grid=self.grid, mask=self.mask, region=self.region)
        else:
            raise RuntimeError(f"Cannot clip by region and mask for data type {type(ds)}")

        return ds

    def validate(self, ds):
        """Validate the cached data to ensure it has data within the region."""
        if isinstance(ds, xr.Dataset):
            # Check to see if the dataset extends roughly the full time series set
            test = clip_region(ds, grid=self.grid, region=self.region, region_dim=self.region_dim)
            test = apply_mask(test, self.mask, grid=self.grid)
            if test.notnull().count().compute() == 0:
                print("""WARNING: The cached array does not have data within
                          the region {self.region}. If you want to continue, set `validate_data=False`""")
                return False
            else:
                return True
        else:
            raise RuntimeError(f"Cannot validate region for data type {type(ds)}")
