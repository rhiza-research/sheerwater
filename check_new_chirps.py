from sheerwater.data.chirps import chirps_gridded
from sheerwater.data.chirps import chirps_v2
import matplotlib.pyplot as plt
from sheerwater.utils.space_utils import clip_region
from sheerwater.utils.region_utils import region_data
from sheerwater.utils import start_remote
if __name__ == "__main__":
    # query chirps v2 on chirps grid
    #start_remote(remote_name='mohini_check_chirps')
    start_time = "2000-01-01"
    end_time = "2000-12-31"
    ds = chirps_gridded(start_time, end_time, grid="chirps", version=3, stations=True)
    # clip to africa
    da = clip_region(ds, region="africa")
    # get africa mask
    import pdb; pdb.set_trace()
    # ds = chirps_v2(start_time, end_time, grid="chirps")
    print(ds)