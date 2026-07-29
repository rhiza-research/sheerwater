WITH cell_avgs AS (
  SELECT
    forecast,
    $region,
    lead_day,
    lat,
    lon,
    COALESCE(
      GREATEST(
        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
    ) AS metric_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    ) AS percent_good_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    ) AS percent_good_members_avg,
    AVG(event_count_year_sum) AS event_count_avg
  FROM (
    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${unimodal_metric_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('obs', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon

    UNION ALL

    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${unimodal_metric_fcst_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('forecast', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon
  ) combined
  GROUP BY forecast, $region, lead_day, lat, lon

  UNION ALL

  SELECT
    forecast,
    $region,
    lead_day,
    lat,
    lon,
    COALESCE(
      GREATEST(
        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
    ) AS metric_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    ) AS percent_good_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    ) AS percent_good_members_avg,
    AVG(event_count_year_sum) AS event_count_avg
  FROM (
    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${unimodal_shifted_metric_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('obs', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon

    UNION ALL

    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${unimodal_shifted_fcst_metric_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('forecast', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon
  ) combined
  GROUP BY forecast, $region, lead_day, lat, lon

  UNION ALL

  SELECT
    forecast,
    $region,
    lead_day,
    lat,
    lon,
    COALESCE(
      GREATEST(
        MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN metric_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN metric_year_avg END)
    ) AS metric_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    ) AS percent_good_avg,
    COALESCE(
      LEAST(
        MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
      ),
      MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
      MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    ) AS percent_good_members_avg,
    AVG(event_count_year_sum) AS event_count_avg
  FROM (
    SELECT forecast, $region, lead_day, lat, lon, 'obs' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${bimodal_metric_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('obs', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon

    UNION ALL

    SELECT forecast, $region, lead_day, lat, lon, 'fcst' AS source,
      AVG((to_jsonb(t)->>'${metric_column}')::double precision) AS metric_year_avg,
      AVG((to_jsonb(t)->>'percent_good')::double precision) AS percent_good_year_avg,
      AVG((to_jsonb(t)->>'percent_good_members')::double precision) AS percent_good_members_year_avg,
      SUM((to_jsonb(t)->>'event_count')::double precision) AS event_count_year_sum
    FROM "${bimodal_metric_fcst_name}" t
    WHERE
      COALESCE(time_grouping, 'None') IN (${time_option})
      AND $region IN (${region_option})
      AND forecast IN (${forecast_option})
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('forecast', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon
  ) combined
  GROUP BY forecast, $region, lead_day, lat, lon
),
thresholds AS (
  SELECT (gs::double precision / 100.0) AS cell_threshold
  FROM generate_series(0, 100, 5) AS gs
),
curve AS (
  SELECT
    t.cell_threshold,
    c.lead_day,
    c.forecast,
    COUNT(*) FILTER (WHERE c.percent_good_avg >= t.cell_threshold) AS good_cells,
    COUNT(c.percent_good_avg) AS points_total
  FROM thresholds t
  CROSS JOIN cell_avgs c
  GROUP BY t.cell_threshold, c.lead_day, c.forecast
),
curve_auc AS (
  SELECT
    forecast,
    lead_day,
    SUM(
      0.5 * (good_cells + next_good_cells) * (next_threshold - cell_threshold)
    ) AS auc_raw,
    -- Informative band: [info_lo, act_lo]; actionable band: [act_lo, 1.0]
    -- (same bands as the threshold-curve subplot shading).
    SUM(
      0.5 * (good_cells + next_good_cells)
        * (LEAST(next_threshold, act_lo) - GREATEST(cell_threshold, info_lo))
    ) FILTER (
      WHERE LEAST(next_threshold, act_lo) > GREATEST(cell_threshold, info_lo)
    ) AS auc_informative_raw,
    SUM(
      0.5 * (good_cells + next_good_cells)
        * (LEAST(next_threshold, 1.0) - GREATEST(cell_threshold, act_lo))
    ) FILTER (
      WHERE LEAST(next_threshold, 1.0) > GREATEST(cell_threshold, act_lo)
    ) AS auc_actionable_raw,
    MAX(points_total) AS points_total,
    MAX(info_lo) AS info_lo,
    MAX(act_lo) AS act_lo
  FROM (
    SELECT
      forecast,
      lead_day,
      cell_threshold,
      good_cells,
      points_total,
      LEAD(cell_threshold) OVER (
        PARTITION BY forecast, lead_day ORDER BY cell_threshold
      ) AS next_threshold,
      LEAD(good_cells) OVER (
        PARTITION BY forecast, lead_day ORDER BY cell_threshold
      ) AS next_good_cells,
      LEAST(
        GREATEST(LEAST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),
        1.0
      ) AS info_lo,
      LEAST(
        GREATEST(GREATEST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),
        1.0
      ) AS act_lo
    FROM curve
  ) steps
  WHERE next_threshold IS NOT NULL
  GROUP BY forecast, lead_day
),
at_cutoff AS (
  SELECT
    forecast,
    lead_day,
    COUNT(CASE WHEN percent_good_avg >= '${actionable_cutoff}'::float THEN 1 END) AS points_above_threshold,
    COUNT(percent_good_avg) AS points_total,
    AVG(event_count_avg) AS event_count_mean
  FROM cell_avgs
  GROUP BY forecast, lead_day
)
SELECT
  a.forecast,
  a.lead_day,
  a.points_above_threshold,
  a.points_total,
  a.event_count_mean,
  c.auc_raw::double precision AS auc_raw,
  -- Expected cells = ∫ good_cells dθ / band width (θ ~ Uniform on the band).
  CASE
    WHEN c.auc_raw IS NULL THEN NULL
    ELSE c.auc_raw::double precision
  END AS auc,
  CASE
    WHEN c.auc_informative_raw IS NULL OR c.info_lo IS NULL OR c.act_lo IS NULL
         OR c.act_lo <= c.info_lo THEN NULL
    ELSE (c.auc_informative_raw / (c.act_lo - c.info_lo))::double precision
  END AS auc_informative,
  CASE
    WHEN c.auc_actionable_raw IS NULL OR c.act_lo IS NULL OR c.act_lo >= 1.0 THEN NULL
    ELSE (c.auc_actionable_raw / (1.0 - c.act_lo))::double precision
  END AS auc_actionable,
  '${gc_view}' AS table_view,
  'no' AS compare_regions,
  '${prob_type}' AS prob_type,
  '${actionable_cutoff}' AS cell_cutoff
FROM at_cutoff a
LEFT JOIN curve_auc c
  ON c.forecast = a.forecast AND c.lead_day = a.lead_day
ORDER BY a.forecast, a.lead_day
