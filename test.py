from sheerwater.utils import start_remote
from sheerwater.spatial_subdivisions import rainfall_region_labels

if __name__ == "__main__":
    start_remote(remote_name="mohini")

    # get rainfall region labels
    rainfall_region_labels = rainfall_region_labels()
    import pdb; pdb.set_trace()

