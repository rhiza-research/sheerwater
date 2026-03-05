import numpy as np
import matplotlib.pyplot as plt
import os
from concurrent.futures import ProcessPoolExecutor

# Create a function to calculate rainfall value at each point


def calculate_rainfall(x, centroids, widths, magnitudes=None):
    """Calculate the rainfall value at each point."""
    total_rainfall = np.zeros(x.shape[0])
    if magnitudes is None:
        magnitudes = np.ones(len(centroids))

    for i in range(len(centroids)):
        # Calculate the distance from each point to the centroid
        distances = np.linalg.norm(x - centroids[i], axis=1)
        total_rainfall += magnitudes[i] * np.exp(-(distances / widths[i]) ** 2)
    return total_rainfall


def run_experiment(args):
    """Run a single experiment."""
    (
        i,
        base_seed,
        n,
        scale,
        s,
        movement,
        n_timesteps,
        velocity_scale,
        birth_rate,
        output_dir,
    ) = args

    np.random.seed(base_seed + i)
    # Generate random centroids between 0 and 1
    initial_centroids = np.random.rand(n, 2)
    widths = scale + np.random.rand(n) * scale * 0.1
    # Variable magnitudes for each centroid
    magnitudes = 0.5 + np.random.rand(n)  # values in [0.5, 1.5)

    # Create a meshgrid of size m x m
    m = 1000
    x = np.linspace(0, 1, m)
    y = np.linspace(0, 1, m)
    X, Y = np.meshgrid(x, y)

    # Add measurement points
    measurements = np.random.rand(s, 2)

    if movement:
        # Assign a random velocity to each centroid so the rain field moves
        velocities = (np.random.rand(n, 2) - 0.5) * velocity_scale

        # Work with Python lists so we can spawn new centroids over time
        centroids_list = [initial_centroids[j, :].copy() for j in range(n)]
        widths_list = [float(widths[j]) for j in range(n)]
        magnitudes_list = [float(magnitudes[j]) for j in range(n)]
        velocities_list = [velocities[j, :].copy() for j in range(n)]

        exp_sensor_vals = []
        exp_cell_vals = []

        for t in range(n_timesteps):
            # Move existing centroids according to their velocities (no periodic boundary)
            for j in range(len(centroids_list)):
                centroids_list[j] = centroids_list[j] + velocities_list[j]

            # Stochastically "birth" new centroids at this time step
            n_births = np.random.poisson(birth_rate)
            for _ in range(n_births):
                centroids_list.append(np.random.rand(2))
                widths_list.append(float(scale + np.random.rand() * scale * 0.1))
                magnitudes_list.append(float(0.5 + np.random.rand()))
                velocities_list.append((np.random.rand(2) - 0.5) * velocity_scale)

            centroids_arr = np.vstack(centroids_list)
            widths_arr = np.array(widths_list)
            magnitudes_arr = np.array(magnitudes_list)

            rainfall = calculate_rainfall(
                np.column_stack([X.ravel(), Y.ravel()]),
                centroids_arr,
                widths_arr,
                magnitudes_arr,
            ).reshape(m, m)
            sensor_rainfall = calculate_rainfall(
                measurements,
                centroids_arr,
                widths_arr,
                magnitudes_arr,
            )

            exp_sensor_vals.append(np.mean(sensor_rainfall))
            exp_cell_vals.append(np.mean(rainfall))

            # Plot the rainfall field and sensors at this time step
            plt.imshow(rainfall, extent=[0, 1, 0, 1], cmap="viridis")
            plt.colorbar()
            plt.scatter(measurements[:, 0], measurements[:, 1], c="red", s=50)
            plt.title(f"Experiment {i}, t={t}")
            plt.savefig(os.path.join(output_dir, f"rainfall_{i}_t{t}.png"))
            plt.close()

        return float(np.mean(exp_sensor_vals)), float(np.mean(exp_cell_vals))

    rainfall = calculate_rainfall(
        np.column_stack([X.ravel(), Y.ravel()]),
        initial_centroids,
        widths,
        magnitudes,
    ).reshape(m, m)
    sensor_rainfall = calculate_rainfall(
        measurements,
        initial_centroids,
        widths,
        magnitudes,
    )

    sensor_avg = float(np.mean(sensor_rainfall))
    cell_avg = float(np.mean(rainfall))

    # Plot the rainfall field and sensors
    plt.imshow(rainfall, extent=[0, 1, 0, 1], cmap="viridis")
    plt.colorbar()
    plt.scatter(measurements[:, 0], measurements[:, 1], c="red", s=50)
    plt.savefig(os.path.join(output_dir, f"rainfall_{i}.png"))
    plt.close()

    return sensor_avg, cell_avg


if __name__ == "__main__":
    sensor_averages = []
    cell_averages = []
    movement = True
    n_timesteps = 10
    velocity_scale = 4.0 # speed of the rain windows / day
    birth_rate = 0.1  # expected number of new centroids per time step

    n_exps = 100

    experiment_name = "scatter_rain"
    if experiment_name == "scatter_rain":
        n = 2
        scale = 0.1
        s = 10
        birth_rate = 1.0
    elif experiment_name == "small_rain":
        n = 1
        scale = 0.1
        s = 200
    elif experiment_name == "large_rain":
        n = 1
        scale = 0.5
        s = 2
    elif experiment_name == "extra_large_rain":
        n = 1
        scale = 2.0
        s = 2

    movement_tag = "moving" if movement else "static"
    name = f"{experiment_name}_{movement_tag}_n{n}_scale{scale}_s{s}_T{n_timesteps if movement else 1}"
    seed = int(np.random.randint(1, 1000000))
    dir = f"rainfall_plots/{name}_seed{seed}_n{n_exps}"

    os.makedirs(dir, exist_ok=True)

    args_list = [
        (i, seed, n, scale, s, movement, n_timesteps, velocity_scale, birth_rate, dir)
        for i in range(n_exps)
    ]

    with ProcessPoolExecutor() as executor:
        for i, (sensor_avg, cell_avg) in enumerate(executor.map(run_experiment, args_list)):
            sensor_averages.append(sensor_avg)
            cell_averages.append(cell_avg)
            if movement:
                print(
                    f"{i} / {n_exps}: "
                    f"Sensor average (time-avg): {sensor_averages[-1]}, "
                    f"Cell average (time-avg): {cell_averages[-1]}"
                )
            else:
                print(
                    f"{i} / {n_exps}: Sensor average: {sensor_averages[-1]}, "
                    f"Cell average: {cell_averages[-1]}"
                )

    # Plot the final scatter plot of sensor averages vs cell averages
    plt.scatter(sensor_averages, cell_averages)

    # Add x-y line
    plt.plot([0, 1], [0, 1], 'k--', label="y = x")

    # Calculate and plot the statistical line of best fit (linear regression)
    sensor_arr = np.array(sensor_averages)
    cell_arr = np.array(cell_averages)
    # Linear regression
    m, b = np.polyfit(sensor_arr, cell_arr, 1)
    xfit = np.linspace(min(sensor_arr), max(sensor_arr), 100)
    yfit = m * xfit + b
    plt.plot(xfit, yfit, 'r-', label='Line of Best Fit')

    plt.xlabel("Sensor Average (mm)")
    plt.ylabel("Cell Average (mm)")
    plt.title(f"Sensor vs Cell Averages: {experiment_name}, {movement_tag}, n={n}, scale={scale}, s={s}, V={velocity_scale}")
    plt.legend()
    plt.savefig(os.path.join(dir, f"sensor_vs_cell_averages_movement_{movement_tag}_n{n}_scale{scale}_s{s}_V{velocity_scale}.png"))
    plt.close()
