### Days Beyond Baseline

Each cell is **cell-days** of expected good cells relative to the selected **Baseline forecast**.

For a forecast F and baseline B, at each lead day L in {7, 14, 21, 28} **where both F and B have usable cells** (`points_total > 0`, i.e. at least one non-null `percent_good`):

1. Compute **expected actionable** (or **informative**) cells for F and B — the average number of good cells when sweeping the cutoff uniformly over the green (actionable) or teal (informative) band on the curve below.
2. Take the difference `(cells_F − cells_B)` and weight by lead day L.

Leads with no usable `percent_good` are **skipped** — they are not treated as zero. In **Events = Both** mode, a lead only counts when both the observation-triggered and forecast-triggered tables have `percent_good` for that forecast (so models like ECMWF IFS ENS are not scored on weeks they do not produce).

**Actionable days** = sum over available leads of `(act[F,L] − act[B,L]) × L`

**Informative days** = sum over available leads of `(info[F,L] − info[B,L]) × L`

Positive values mean more expected good cells than the baseline, with later leads weighted more heavily. The baseline row is always `0`. ★ marks the best (highest) value in each column.

Other **View** options show expected cells by lead day instead of these summary KPIs.
