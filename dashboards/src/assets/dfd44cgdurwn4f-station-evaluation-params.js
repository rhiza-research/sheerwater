// EXTERNAL({"panel_id":"station-evaluation","key":"params"}):dfd44cgdurwn4f-station-evaluation-params.js
const STATIONEVAL_TIME_FILTER_OUTPUT_MODE = "MXX";

const readVars = () => {
    const truth = readVar("truth", "ghcn");
    const product = readVar("product", "precip");
    return {
        forecast: readVar("reanalysis", "era5"),
        grid: readVar("grid"),
        metric: readVar("metric", "mae"),
        product: resolveMetricProduct(product, truth),
        lead: readVar("lead", "week1"),
        timeGrouping: readVar("time_grouping"),
        timeFilter: readVar("time_filter", "None"),
        timeFilterOutputMode: STATIONEVAL_TIME_FILTER_OUTPUT_MODE,
        aggDays: readVar("agg_days", "7"),
        datasetFamily: "metric",
        vmin: readVar("vmin", ""),
        vmax: readVar("vmax", ""),
    };
};

function resolveRegion(_) {
    return "global";
}
