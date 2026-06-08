from sheerwater.utils import start_remote
from sheerwater.spatial_subdivisions.spatial_subdivisions import rainfall_region_labels, season_region_labels, space_grouping_labels
import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_remote(remote_name='cache_spatial')

    grid = 'global1_5'
    # rainfall region labels
    rr15 = rainfall_region_labels(grid=grid, recompute=True)
    fig, axs = plt.subplots(4, 1, figsize=(10, 10))
    (rr15.region == 'east_africa_sudanian').plot(x="lon", ax=axs[0])
    (rr15.region == 'east_africa_lake_victoria_basin').plot(x="lon", ax=axs[1])
    (rr15.region == 'east_africa_coastal_savannah').plot(x="lon", ax=axs[2])
    (rr15.region == 'east_africa_west_ethiopian_highlands').plot(x="lon", ax=axs[3])


    # season region labels
    sr15 = season_region_labels(grid='global1_5', recompute=True)
    sr25 = season_region_labels(grid='global0_25', recompute=True)

    import pdb; pdb.set_trace()
    # season region labels
    sl1 = space_grouping_labels(grid=grid, space_grouping='rainfall_region', recompute=True)
    sl2 = space_grouping_labels(grid=grid, space_grouping='season_regions', recompute=True)
    sl12 = space_grouping_labels(grid=grid, space_grouping=['rainfall_region', 'country'], recompute=True)
    sl12 = space_grouping_labels(grid=grid, space_grouping=['season_regions', 'country'], recompute=True)

    # spatial