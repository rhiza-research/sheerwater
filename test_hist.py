import xarray as xr
import numpy as np
from sheerwater.utils import start_remote
from sheerwater.data import imerg
from sheerwater.data import tahmo
from sheerwater.utils.time_utils import groupby_time
from sheerwater.metrics import paired_histogram

if __name__ == "__main__":
    start_remote()
    # try paired histogram
    hist2d = paired_histogram(start_time="2019-01-01", end_time="2019-03-31", time_grouping="month", space_grouping="country",estimate="imerg", truth="tahmo", agg_days=7, grid="global1_5", mask="lsm", region="africa", recompute=True)
    import pdb; pdb.set_trace()
    
    
    
    ph = paired_histogram(start_time="2019-01-01", end_time="2019-03-31", estimate="imerg", truth="tahmo", agg_days=7, grid="global0_25", mask="lsm", region="africa")
    import pdb; pdb.set_trace()
    # try paired histogram
    imerg_data = imerg(start_time="2019-01-01", end_time="2019-03-31", agg_days=7, grid="global0_25", mask="lsm", region="africa")
    tahmo_data = tahmo(start_time="2019-01-01", end_time="2019-03-31", agg_days=7, grid="global0_25", mask="lsm", region="africa")
    # merge datasets
    # rename precip variables
    imerg_data = imerg_data.rename({'precip': 'imerg_precip'})
    tahmo_data = tahmo_data.rename({'precip': 'tahmo_precip'})
    # merge datasets
    merged_data = xr.merge([imerg_data, tahmo_data])
    # get paired histogram
    paired_hist = groupby_time(merged_data, 'month', "paired_hist", bins=np.arange(0, 100, 1), variables=['imerg_precip', 'tahmo_precip'])
    import pdb; pdb.set_trace()


    imerg_data = imerg(start_time="2019-01-01", end_time="2019-03-31", agg_days=7, grid="global0_25", mask="lsm", region="africa")

    # try grouping in hist bins
    imerg_hist = groupby_time(imerg_data, 'month', "hist", bins=np.arange(0, 100, 1))
    import pdb; pdb.set_trace()