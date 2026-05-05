from sheerwater.metrics import metric
from sheerwater.utils import start_remote
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


if __name__ == "__main__":
    # call pod on africa
    start_remote(remote_name = "mohini")

    # time parameters
    start_time = "2015-01-01"
    end_time = "2024-12-31"

    # spatial parameters
    region = "africa"
    spatial = True
    grid = "global0_25"

    # event definition
    agg_days = 5
    forecast = "imerg"
    truth = "tahmo"
    variable = "precip"
    threshold = 2

    thresholds = [0.1, 0.5, 2, 5, 10]
    good_counts = []
    for threshold in thresholds:
        print(f"Processing threshold: {threshold}")
        pod = metric(start_time=start_time, end_time=end_time, 
        variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"pod-{threshold}",
        region=region, spatial=spatial, time_grouping=None, grid=grid)
        far = metric(start_time=start_time, end_time=end_time, 
        variable=variable, agg_days=agg_days, forecast=forecast, truth=truth, metric_name=f"far-{threshold}",
        region=region, spatial=spatial, time_grouping=None, grid=grid)

        # remove space_grouping and spatial_ref dims
        pod = pod.drop_vars(['space_grouping', 'spatial_ref'])
        far = far.drop_vars(['space_grouping', 'spatial_ref'])

        above_pod = 0.9
        below_far = 0.2
        # identify cells where pod is within good_pod and far is within good_far
        mask = (pod.pod >= above_pod) & (far.far <= below_far)
        mask = mask.where(~(pod.pod.isnull() | far.far.isnull()))
        ct = float(mask.sum(skipna=True).values)
        good_counts.append(ct)
    import pdb; pdb.set_trace()

    
    cmap = ListedColormap(["red", "green"])
    cmap.set_bad("white")
    mask.astype(float).plot(x="lon", y="lat", cmap=cmap, vmin=0, vmax=1)
    plt.title(f"POD > {above_pod} and FAR < {below_far} w. {threshold} mm over {agg_days} days")
    plt.show()
    import pdb; pdb.set_trace()


    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    pod.pod.plot(ax=axs[0], x="lon", vmin=0.9, vmax=1.0)
    far.far.plot(ax=axs[1], x="lon", vmin=0.0, vmax=0.2)
    plt.title(f"POD/FAR at {threshold} mm over {agg_days} days")
    plt.show()
    import pdb; pdb.set_trace()