from sheerwater.utils import start_remote
from sheerwater.interfaces import get_data
from sheerwater.utils.data_utils import regrid
from sheerwater.utils.time_utils import assign_grouping_coordinates
from sheerwater.spatial_subdivisions import space_grouping_labels

if __name__ == "__main__":
    start_remote(remote_name = "qq_mohini")
    
    input = "imerg_final"
    target = "tahmo_avg"
    input_grid = "global1_5"
    output_grid = "global0_25"

    space_window = "admin_0"
    time_window = "month_of_year"

    start_time = "2015-01-01"
    end_time = "2024-12-31"
    variable = "precip"
    agg_days = 5
    mask = "lsm"
    region = "ghana"

    import pdb; pdb.set_trace()
    input_ds = get_data(input)(start_time, end_time, variable, agg_days=agg_days, grid=input_grid, mask=mask, region=region)
    target_ds = get_data(target)(start_time, end_time, variable, grid=output_grid, mask=mask, region=region)
    # regrid to output grid using method nearest
    input_ds = regrid(input_ds, output_grid, method="nearest")
    # group target by time and space window and create rank index
    # add time_grouping labels
    input_ds = assign_grouping_coordinates(input_ds, time_window, "time")
    # add space_grouping labels
    space_labels = space_grouping_labels(grid=output_grid, space_grouping=space_window)
    input_ds = input_ds.assign_coords(space_window=space_labels.region)











