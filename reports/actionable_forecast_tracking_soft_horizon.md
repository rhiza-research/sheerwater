# Nimbus Advanced Agricultural Benchmarking

**Sheerwater Benchmark · Method Note**  
August 2026 · ~2 pages

**TL;DR.** **Actionable days beyond baseline**: for each grid cell, take the longest lead at which it still meets the actionable percent-good cutoff, subtract the same horizon for the baseline, then average over all cells in the selected country or countries.

---

## 1. Motivation

Agricultural users do not experience forecast skill as a single scorecard number. They care whether a forecast remains **good enough** over a useful fraction of the landscape, and how far into the future that usefulness extends. The Sheerwater **Actionable Forecast Tracking** dashboard therefore summarizes event-based verification as:

1. how many grid cells clear a chosen quality cutoff at each lead (**good cells at a cutoff**), and  
2. how far each cell’s skill extends in lead time relative to a baseline (**days beyond baseline**).

This note defines both quantities and how to interpret them.

### Observation-triggered and forecast-triggered events

For event metrics such as extreme rain days and dry spells, an event can be defined from the observations or from the forecast. We score both:

- **Observation-triggered:** events found in the observations. Poor scores here are *false negatives*: the event happened, but the forecast missed it.
- **Forecast-triggered:** events found in the forecast. Poor scores here are *false positives*: the forecast warned of an event that was not observed.

KR Tracking’s default “both” mode combines the two by taking the **worse** of the observation-triggered and forecast-triggered scores at each cell and lead (maximum error, or minimum percent-good). A forecast cannot look good by catching observed events while over-warning, or by staying quiet while missing real events.

## 2. Setup

For a chosen agricultural event metric (e.g. dry-spell or extreme-rain skill with an actionable error bar), each forecast **F**, lead day **L**, and grid cell has a **percent-good** score between 0 and 1: the fraction of verified events meeting the metric’s good threshold.

Fix two cutoffs on that score (evaluated as **points**, not as bands):

| Cutoff | Symbol | Intent |
|--------|--------|--------|
| **Informative** | θ_info | Useful signal |
| **Actionable** | θ_act | Decision-grade bar |

Typical defaults are θ_info = 0.50 and θ_act = 0.75. Leads considered for the horizon KPI are the first four weekly horizons:

`L ∈ {7, 14, 21, 28}`

A cell **passes** cutoff θ at lead L when its percent-good is at least θ.

## 3. Good cells at a cutoff

At a fixed lead L, define:

`G_F(L, θ) = number of cells with percent-good ≥ θ`

The dashboard’s threshold curve plots `G_F(L, θ)` versus θ. The Informative and Actionable markers are narrow guides at θ_info and θ_act. The lead-panel deltas are simply the difference in cell counts versus baseline B:

`ΔG(L, θ) = G_F(L, θ) − G_B(L, θ)`  → reported as **number of cells**

Optional table views also report `G_F(L, θ_info)` and `G_F(L, θ_act)` directly (“Cells @ Informative / Actionable”). A separate “Expected Cells” view still averages `G_F` over the full cutoff axis from 0 to 1; that is a curve summary, not the days-beyond KPI.

## 4. Days beyond baseline

Days beyond baseline answers: *relative to the baseline, how much farther in lead time does this forecast stay good enough?*

### Per cell

For each grid cell **c** and cutoff θ (either θ_info or θ_act), define the **horizon** as the longest lead at which the cell still passes:

`H_F(c, θ) = max { L ∈ {7, 14, 21, 28} : percent-good_F(c, L) ≥ θ }`

or `0` if the cell never clears θ at those leads. A null percent-good at a lead is a noop: that lead is dropped for both F and B on the cell (horizons use only shared usable leads). It is not treated as a fail.

The cell’s days beyond baseline are:

`D_F(c, θ) = H_F(c, θ) − H_B(c, θ)`

with both horizons computed on the intersection of leads where F and B have usable percent-good. Cells with no shared usable leads are omitted from the mean.

### Region summary

Regions are selectable as a single country or multiple countries. The reported value is the **mean over all grid cells** in the selected country or countries:

`Days(F, B; θ) = (1 / n) × Σ_c D_F(c, θ)`

where the sum runs over the `n` comparable cells in that selection. Separate values are shown for Informative (θ_info) and Actionable (θ_act). The baseline column is always `0`. Forecasts with no overlapping usable cells show as missing (—), not as zero (so short-range or sparse models are not scored as “tied with baseline”).

Against a baseline with horizon 0 everywhere, that mean is easy to read: every cell actionable out to lead 28 gives +28; every cell actionable only at lead 7 gives +7; if 3 of 15 cells are actionable out to lead 14 and the rest are unchanged, the region mean is 3 × 14 / 15 = +2.8; and matching the baseline everywhere gives 0. A cell-level +14 means that cell clears the cutoff two weeks farther than the baseline on that same cell.

## 5. Limitations and next steps

- **Training / testing conflict.** Several ML forecasts were trained on years that overlap the evaluation period (e.g. training through 2021), so KR Tracking scores can be optimistic relative to a true out-of-sample holdout. *Planned:* a rolling overfit sensitivity study that varies the evaluation window relative to each model's training cutoff.
- **Probabilistic evaluation.** Ensemble forecasts are scored per member and then averaged, which captures **expected** error across the ensemble rather than the true error of a single realized forecast or a proper score of the full distribution. *Planned:* compute a median event from the ensemble, then evaluate that deterministic event.
- **Equal cell weighting.** Regional means treat every grid cell equally, so empty or sparsely farmed cells weigh as much as intensive agricultural areas. *Planned:* weight cells by arable land or farming population.
- **Discrete weekly leads.** Horizons are evaluated only at four leads (`L ∈ {7, 14, 21, 28}`: weeks 1–4). Sub-weekly skill is ignored: a cell that remains good enough out to day 10 is still tracked as horizon 7. *Planned:* denser lead sampling (e.g. daily or every few days) so mid-week gains are counted.

---

Implemented in the [KR Tracking dashboard](https://dashboards.rhizaresearch.org/d/ee4mze492j0n4d/home?orgId=1&from=now-6h&to=now&timezone=utc).
