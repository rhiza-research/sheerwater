---
name: aggregate-temporal
description: Apply a rolling temporal aggregation (mean or sum over an N-step window) to a Rhiza Envelope Zarr along the time or step axis. Use when you need to convert daily data to dekadal, weekly, or other rolling aggregates before evaluation or plotting.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI.
metadata:
  openclaw:
    requires:
      bins:
        - uv
---

# aggregate-temporal

Rolling temporal aggregation, left-aligned. Backed by `sheerwater.utils.data_utils.roll_and_agg`. The aggregation coordinate must be `datetime64` (`time`) or `timedelta64` (`step`/`prediction_timedelta`).

The aggregator drops the first `agg-1` slices (which would be all NaN) and shifts the remaining slices' coordinate values left by `agg-1` days so each window is labeled by its first day.

## When to use

- Converting daily envelope data to weekly/dekadal/monthly rolling aggregates.
- Aligning a fine-cadence forecast to a coarser truth window before metric computation.

## Usage

```
uvx sheerwater@latest ops aggregate \
    --input <in.zarr> \
    --agg N \
    [--agg-col time|step] [--agg-fn mean|sum] [--agg-thresh K] \
    --output <out.zarr>
```

### Key flags

- `--input`, `-i` — input Zarr.
- `--agg` — window length in coordinate steps (e.g. 7 for weekly daily input, 10 for dekadal).
- `--agg-col` — coordinate to roll over. Default `time`. For forecasts use `prediction_timedelta` (or whatever step coordinate the input uses).
- `--agg-fn` — `mean` (default) or `sum`. Use `sum` for precipitation totals; `mean` for state variables.
- `--agg-thresh` — minimum number of valid (non-NaN) points required per window (default = `--agg`, i.e. require all points). Lower this to allow partial windows.

### Output

Zarr with the rolling aggregate applied. Stamped with `rhiza_aggregation` (e.g. `7-time-sum`).

## Example

```bash
uvx sheerwater@latest ops aggregate --input /tmp/chirps_daily.zarr --agg 7 --agg-fn sum \
    --output /tmp/chirps_weekly_sum.zarr
```
