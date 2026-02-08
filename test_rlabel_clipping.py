from sheerwater.spatial_subdivisions import space_grouping_labels, clip_region
from sheerwater.masks import spatial_mask
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()

    grid = "global1_5"
    space_grouping = "country"
    region = "africa"
    mask = "lsm"
    
    # get spatial mask for data
    space_grouping_ds = space_grouping_labels(grid=grid, space_grouping=space_grouping).compute()
    import pdb; pdb.set_trace()
    mask_ds = spatial_mask(mask=mask, grid=grid, memoize=True)
    if region != 'global':
        space_grouping_ds = clip_region(space_grouping_ds, region, grid=grid, clip_coords=True)
        mask_ds = clip_region(mask_ds, region, grid=grid)
    import pdb; pdb.set_trace()