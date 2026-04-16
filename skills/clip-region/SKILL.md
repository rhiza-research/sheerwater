---
name: clip-region
description: Spatially subset a gridded Rhiza Envelope Zarr to a named sheerwater region (country, custom region, agroecological zone, etc.). Use when you need to restrict a dataset to a country or named area before downstream aggregation, plotting, or evaluation.
license: MIT
compatibility: Requires Python 3.12+, uv, and the `sheerwater` CLI.
metadata:
  openclaw:
    requires:
      bins:
        - uv
---

# clip-region

Region-aware clipping using sheerwater's named regions and grid-aware spatial subdivisions. Backed by `sheerwater.spatial_subdivisions.clip_region`. The CLI passes a single region NAME (not a subdivision level) and sheerwater auto-detects which subdivision the name belongs to.

## Region naming

Regions live under one of these subdivision levels (defined in `spatial_subdivisions.py`):

| Subdivision | Examples |
|---|---|
| `country` | `kenya`, `ethiopia`, `ghana`, `united_states_of_america`, ... (NaturalEarth `world_50m` admin-0 set, ~250 entries) |
| `admin_1` | sub-national admin-1 boundaries; names are formatted `<country>-<admin1>` (e.g. `kenya-rift_valley`) |
| `admin_2` | admin-2 boundaries; names are `<country>-<admin1>-<admin2>` |
| `continent` | `africa`, `asia`, `europe`, ... (UN/WB world definitions) |
| `subregion`, `region_un`, `region_wb` | Other UN/WB groupings |
| `sheerwater_region` | Custom region groupings: `nimbus_east_africa` (kenya/burundi/rwanda/tanzania/uganda), `nimbus_west_africa` (16 W African countries), `conus` (USA) |
| `meteorological_zone` | `tropics`, `extratropics_northern`, `extratropics_southern` |
| `hemisphere` | `northern_hemisphere`, `southern_hemisphere` |
| `agroecological_zone` | FAO AEZ classes, e.g. `tropics_lowland_humid`, `tropics_highland_semi-arid`, ... (33 classes plus no_region) |
| `global` | `global` (the whole grid; this is a no-op) |

Sheerwater normalizes region names: lowercases, replaces spaces with underscores, strips accents, and applies a small set of country-name aliases (e.g. `cote_d'ivoire` → `ivory_coast`, `swaziland` → `eswatini`). Pass the human name and sheerwater will reconcile.

## When to use

- Narrowing a global or continental envelope down to one country, region, or zone before plotting or per-region reporting.
- Restricting any gridded envelope to a named region before downstream operations.

## Usage

```
uvx sheerwater@latest ops clip \
    --input <in.zarr> \
    --region NAME \
    --grid GRID \
    --output <out.zarr>
```

### Key flags

- `--input`, `-i` — input Zarr.
- `--region` — region NAME (any of the names listed above; not a subdivision name).
- `--grid` — grid the region is defined against (e.g. `global0_25`, `global1_5`, `global0_1`, `global0_05`, `salient0_25`). Must match the grid the input was fetched on, since the region masks are pre-computed per-grid.
- `--output`, `-o` — output Zarr.

### Output

Same dims and variables as input, restricted to the requested region. Stamped with `rhiza_region`.

## Example

```bash
uvx sheerwater@latest ops clip --input /tmp/era5.zarr --region kenya --grid global0_25 \
    --output /tmp/era5_kenya.zarr
```

```bash
# Clip to a custom multi-country region
uvx sheerwater@latest ops clip --input /tmp/era5.zarr --region nimbus_east_africa --grid global0_25 \
    --output /tmp/era5_east_africa.zarr
```
