[comment]: # (EXTERNAL:metrics_explainer.md)
### Selected Metric: {{#if (eq metric "mae")}}MAE {{/if}} {{#if (eq metric "rmse")}}RMSE{{/if}} {{#if (eq metric "crps")}}CRPS{{/if}} {{#if (eq metric "bias")}}Bias{{/if}} {{#if (eq metric "smape")}}SMAPE{{/if}} {{#if (eq metric "seeps")}}SEEPS{{/if}} {{#if (eq metric "acc")}}ACC{{/if}}  {{#if (eq metric "heidke-1-5-10-20")}}Heidke 1/5/10/20mm{{/if}} {{#if (eq metric "far-1")}}FAR 1mm{{/if}} {{#if (eq metric "far-5")}}FAR 5mm{{/if}} {{#if (eq metric "far-10")}}FAR 10mm{{/if}} {{#if (eq metric "pod-1")}}POD 1mm{{/if}} {{#if (eq metric "pod-5")}}POD 5mm{{/if}} {{#if (eq metric "pod-10")}}POD 10mm{{/if}} {{#if (eq metric "ets-1")}}ETS 1mm{{/if}} {{#if (eq metric "ets-5")}}ETS 5mm{{/if}} {{#if (eq metric "ets-10")}}ETS 10mm{{/if}} {{#if (eq metric "early_season_accumulation-30d")}}Early Season 30 day Accumulation (MAE){{/if}}{{#if (eq metric "big_rain_days")}}Large rain days (SMAPE){{/if}} {{#if (eq metric "in_season_dry_spell")}}In season dry spells (forecasted value){{/if}}




{{#if (eq metric "early_season_accumulation-30d")}}
The early season accumulation metric finds the point in every season at which *100mm* of rainfall accumulates. It then computes the MAE of the last 30 days of rainfall in both the observatoins and the forecast. For forecast lead times less than 30 days, forecasts are appended to the end of the observations. Seasons are handled based on regional seasonal classifications.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower MAE means better predictions. We believe results less than about 25mm indicate good start of season predictability.</span> 

{{else if (eq metric "big_rain_days")}}
Large rain days detects individual days where the rainfall exceeds 15mm. It then takes the SMAPE of the 5 day period around those days (+/- 2 days). A period is taken around
the rain days to allow for slight miss-timing of the rain in the forecast and the ground truth. SMAPE is chosen to smoothly allow for more error in larger rainfall events.
The top row is triggered on large rain days observed in the observations (high SMAPE means the forecast failed to forecast rain when it was observed). The bottom row is triggered on large rain days observed in the forecast (high SMAPE means the forecast placed rain where it wasn't observed.)\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower SMAPE means better predictions. We expect SMAPEs below 0.2-0.3 indicate good 
prediction of above-average rainfall events.</span> 

{{else if (eq metric "in_season_dry_spell")}}
The in season dry spells event finds the start of season by looking for the first rainy day within 45 days of the observations reaching 10% of the total accumulated rainfall for a season. It looks for dry spells until 40% of the rainfall has accumulated for the season. Dry spells are defined as any 10 day period with less than 15mm of total rain. We present
the total forecasted rainfall in this period. The top row shows performance for dry spells in the observations (high rainfall means the forecast predicted rain when the observations were dry - a wet biased forecast). The top row shows performance for dry spells in the forecast (high rainfall means that rain occured when the forecast predicted dry - a dry biased forecast).\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower rainfall means better predictions in dry periods. We believe rainfall below about 20mm-30mm over the 10 day period to be good.</span> 

{{else if (eq metric "mae")}}
Mean absolute error (MAE) measures the average magnitude of the errors in a set of predictions, without considering
their direction.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower MAE means better predictions.</span> 

{{else if (eq metric "crps")}}
Continuous ranked probability score (CRPS) assesses the accuracy of probabilistic forecasts by comparing the cumulative
distribution function of forecasts to the observed values.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower CRPS indicates better probabilistic forecasting skill.</span>

{{else if (eq metric "rmse")}}
Root mean squared error (RMSE) gives higher weight to large errors, making it more sensitive to outliers.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower RMSE means better predictions.</span>

{{else if (eq metric "acc")}}
Anomaly correlation coefficient (ACC) ACC is a measure of how well the forecast anomalies have represented the observed anomalies
relative to climatology. We used 1991-2020 climatology (years inclusive) for our ACC calculation.\
<span style="color: green; font-weight: bold;">🟢 Larger is better — higher ACC means better predictions. Range [-1, 1].</span>

{{else if (eq metric "bias")}}
Bias measures the signed magnitude of errors in a set of predictions. \
<span style="color: gray; font-weight: bold;">⚪ Ideal value = 0.0 — Bias should be close to 0.0 for an unbiased forecast.</span>

{{else if (eq metric "smape")}}
Symmetric mean absolute percentage error (SMAPE) is a normalized version of Mean Absolute Percentage Error (MAPE) and calculate sthe error as a percentage of the total value. We only calculate SMAPE for precipitation.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower SMAPE indicates better forecasting accuracy. Range [0, 1].</span>

{{else if (eq metric "seeps")}}
Stable equitable error in probability space (SEEPS) is a score designed for evaluating rainfall forecasts while taking into account climactic difference in rainfall. Areas that are too dry or wet are exclued. 
We include all cells with a 3-93% non-dry day frequency to ensure inclusion of relevant parts of Africa. We only calculate SEEPS for precipitation.\
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower SEEPS indicates better forecasting accuracy. Good SEEPS for short term forecasts on cells that have 10-85% non-dry days are considered between 0-1.</span>

{{else if (eq metric "heidke-1-5-10-20")}}
Heidke skill score (HSS) compares the accuracy of a forecast to random chance for a set of predetermined rainfall thresholds—in this case, 1, 5, 10, and 20mm. We only calculate Heidke for precipitation.\
<span style="color: green; font-weight: bold;">🟢 Larger is better — a higher HSS indicates better skill. Range [-&infin;, 1]</span>

{{else if (or (eq metric "pod-1") (or (eq metric "pod-5") (eq metric "pod-10")))}}
Probability of detection (POD) measures the fraction of observed rainfall events that were correctly predicted—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate POD for precipitation. \
<span style="color: green; font-weight: bold;">🟢 Larger is better — higher probability of detection is better. Range [0, 1]. </span>

{{else if (or (eq metric "far-1") (or (eq metric "far-5") (eq metric "far-10")))}}
False alarm rate (FAR) quantifies the fraction of predicted rainfall events that were not observed—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate FAR for precipitation.\ 
<span style="color: red; font-weight: bold;">🔴 Smaller is better — lower false alarm rate is better. Range [0, 1].</span>

{{else if (or (eq metric "ets-1") (or (eq metric "ets-5") (eq metric "ets-10")))}}
Equitable threat score (ETS) measures a combination of POD and FAR while accounting for random chance on a specific event—in this case, a weekly average daily rainfall of over 1, 5, or 10mm. We only calculate ETS for precipitation. \
<span style="color: green; font-weight: bold;">🟢 Larger is better — higher ETS indicates better skill. Range [-1/3, 1].</span>

{{else}}
_no description available for this metric._
{{/if}}
