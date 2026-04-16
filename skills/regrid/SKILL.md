---
name: regrid
description: Regrid a gridded Rhiza Envelope Zarr to a different sheerwater grid (e.g. global0_25 → global1_5), with a choice of regridding methods. Use when two datasets need to be on the same grid before per-cell comparison, or when reducing spatial detail for faster downstream steps.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI.
metadata:
  openclaw:
    requires:
      bins:
        - uv
---

# regrid

Spatial regridding using `xarray-regrid`. Backed by `sheerwater.utils.data_utils.regrid`. Targets sheerwater's named grids.

## Available grids

| Grid name | Resolution | Notes |
|---|---|---|
| `global0_05` | 0.05° | Finest currently-defined sheerwater grid |
| `global0_1` | 0.1° | IMERG / ERA5-Land native |
| `global0_25` | 0.25° | ERA5 ARCO native; common default |
| `global1_5` | 1.5° | ECMWF / FuXi / GenCast / GraphCast (fine path) native |
| `salient0_25` | 0.25° | Salient grid offset variant |

Plus dataset-specific named grids accepted by the source loaders (`tamsat`, `chirps`, `source` for native).

## Methods

`--method` selects the regridding algorithm:

- `linear` — bilinear interpolation
- `nearest` — nearest neighbor
- `cubic` — cubic interpolation
- `conservative` — area-weighted; preferred for flux-like fields (precipitation, radiation)
- `most_common` — modal value; preferred for categorical fields (region labels, AEZ classes)

## When to use

- Putting two datasets on the same grid before per-cell comparison or metric computation.
- Reducing spatial resolution for faster plotting or aggregation.
- Increasing apparent resolution for visualization (interpolation only — does not produce new fine-scale information).

## Usage

```
uvx sheerwater@latest ops regrid \
    --input <in.zarr> \
    --grid OUTPUT_GRID \
    [--method conservative] [--base base180] [--region global] \
    --output <out.zarr>
```

### Key flags

- `--input`, `-i` — input Zarr.
- `--grid` — output grid name from the table above.
- `--method` — `linear`, `nearest`, `cubic`, `conservative` (default), or `most_common`.
- `--base` — longitude base of the output grid: `base180` (default, [-180, 180]) or `base360` ([0, 360]).
- `--region` — clip the output grid to a region after regridding (default `global`).

### Output

Zarr on the new grid with the same variables.

## Example

```bash
uvx sheerwater@latest ops regrid --input /tmp/era5_0_25.zarr --grid global1_5 --method conservative \
    --output /tmp/era5_1_5.zarr
```
