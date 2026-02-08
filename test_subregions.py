from sheerwater.metrics import coverage
from sheerwater.utils import start_remote

if __name__ == "__main__":
    start_remote()
    # get coverage for africa by subregion
    #coverage_table/grid_global1_5/region_africa/space_grouping_None/stations_ghcn_avg/time_grouping_year/variable_precip requested
    ds = coverage(start_time="2012-01-01", end_time="2025-01-01", variable="precip", agg_days=7, 
                        station_data="ghcn_avg", time_grouping=None, space_grouping="country", grid="global1_5", mask="lsm", region="africa",
                        recompute=True)
    df = ds.to_dataframe()
    import pdb; pdb.set_trace()
