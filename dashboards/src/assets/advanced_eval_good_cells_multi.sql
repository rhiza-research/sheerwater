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
    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast
    -- side would otherwise fall back to obs-only percent_good and look like a
    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    END AS percent_good_avg,
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    END AS percent_good_members_avg,
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast
    -- side would otherwise fall back to obs-only percent_good and look like a
    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    END AS percent_good_avg,
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    END AS percent_good_members_avg,
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
    -- In 'both' mode PostgreSQL LEAST() ignores NULLs, so a missing forecast
    -- side would otherwise fall back to obs-only percent_good and look like a
    -- real (bad) score. Require both sides; otherwise leave null so the lead drops out.
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_year_avg END)
    END AS percent_good_avg,
    CASE
      WHEN '${source}' = 'both' THEN
        CASE
          WHEN MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END) IS NOT NULL
           AND MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END) IS NOT NULL
          THEN LEAST(
            MAX(CASE WHEN source = 'obs'  THEN percent_good_members_year_avg END),
            MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
          )
          ELSE NULL
        END
      WHEN '${source}' = 'obs' THEN
        MAX(CASE WHEN source = 'obs' THEN percent_good_members_year_avg END)
      ELSE
        MAX(CASE WHEN source = 'fcst' THEN percent_good_members_year_avg END)
    END AS percent_good_members_avg,
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
      AND (
        '$__all' IN (${region_option})
        OR '__all__' IN (${region_option})
        OR $region IN (${region_option})
      )
      AND (forecast IN (${forecast_option}) OR forecast = '${baseline_forecast}')
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
cutoffs AS (
  SELECT
    LEAST(
      GREATEST(LEAST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),
      1.0
    ) AS info_lo,
    LEAST(
      GREATEST(GREATEST('${informative_cutoff}'::float, '${actionable_cutoff}'::float), 0.0),
      1.0
    ) AS act_lo
),
-- Pooled curve over all selected-region cells (for expected-cells views).
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
    MAX(points_total) AS points_total
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
      ) AS next_good_cells
    FROM curve
  ) steps
  WHERE next_threshold IS NOT NULL
  GROUP BY forecast, lead_day
),
-- Good-cell counts at the Informative and Actionable cutoff points (not band averages).
at_cutoff AS (
  SELECT
    c.forecast,
    c.lead_day,
    COUNT(*) FILTER (
      WHERE c.percent_good_avg >= k.act_lo
    ) AS points_above_threshold,
    COUNT(*) FILTER (
      WHERE c.percent_good_avg >= k.info_lo
    ) AS points_above_informative,
    COUNT(c.percent_good_avg) AS points_total,
    AVG(c.event_count_avg) AS event_count_mean
  FROM cell_avgs c
  CROSS JOIN cutoffs k
  GROUP BY c.forecast, c.lead_day
),
-- Per-cell pass/fail at each cutoff point.
cell_frac AS (
  SELECT
    c.forecast,
    c.lead_day,
    c.lat,
    c.lon,
    CASE WHEN c.percent_good_avg >= k.act_lo THEN 1.0 ELSE 0.0 END AS frac_actionable,
    CASE WHEN c.percent_good_avg >= k.info_lo THEN 1.0 ELSE 0.0 END AS frac_informative
  FROM cell_avgs c
  CROSS JOIN cutoffs k
  WHERE c.lead_day IN (7, 14, 21, 28)
    AND c.percent_good_avg IS NOT NULL
),
-- Per-cell days beyond baseline, using only leads where BOTH F and B have
-- non-null percent_good for that cell. A null lead is a noop (skipped).
-- Horizons are longest shared lead that still meets each cutoff.
cell_days AS (
  SELECT
    f.forecast,
    f.lat,
    f.lon,
    (
      COALESCE(MAX(f.lead_day) FILTER (WHERE f.frac_actionable = 1.0), 0)
      - COALESCE(MAX(b.lead_day) FILTER (WHERE b.frac_actionable = 1.0), 0)
    )::double precision AS act_days,
    (
      COALESCE(MAX(f.lead_day) FILTER (WHERE f.frac_informative = 1.0), 0)
      - COALESCE(MAX(b.lead_day) FILTER (WHERE b.frac_informative = 1.0), 0)
    )::double precision AS info_days
  FROM cell_frac f
  INNER JOIN cell_frac b
    ON b.forecast = '${baseline_forecast}'
   AND b.lat = f.lat
   AND b.lon = f.lon
   AND b.lead_day = f.lead_day
  GROUP BY f.forecast, f.lat, f.lon
),
cell_days_summary AS (
  SELECT
    forecast,
    MIN(act_days)::double precision AS act_min,
    AVG(act_days)::double precision AS act_avg,
    MAX(act_days)::double precision AS act_max,
    MIN(info_days)::double precision AS info_min,
    AVG(info_days)::double precision AS info_avg,
    MAX(info_days)::double precision AS info_max,
    COUNT(*)::double precision AS n_cells
  FROM cell_days
  GROUP BY forecast
)
SELECT
  a.forecast,
  a.lead_day,
  a.points_above_threshold::double precision AS points_above_threshold,
  a.points_total::double precision AS points_total,
  a.event_count_mean::double precision AS event_count_mean,
  CASE
    WHEN a.points_total IS NULL OR a.points_total = 0 OR c.auc_raw IS NULL THEN NULL
    ELSE c.auc_raw::double precision
  END AS auc_raw,
  CASE
    WHEN a.points_total IS NULL OR a.points_total = 0 OR c.auc_raw IS NULL THEN NULL
    ELSE c.auc_raw::double precision
  END AS auc,
  a.points_above_informative::double precision AS auc_informative,
  a.points_above_threshold::double precision AS auc_actionable,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.act_min
  END AS act_min,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.act_avg
  END AS act_avg,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.act_max
  END AS act_max,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.info_min
  END AS info_min,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.info_avg
  END AS info_avg,
  CASE
    WHEN a.forecast = '${baseline_forecast}' THEN 0::double precision
    ELSE d.info_max
  END AS info_max,
  d.n_cells,
  '${gc_view}' AS table_view,
  'no' AS compare_regions,
  '${prob_type}' AS prob_type,
  '${actionable_cutoff}' AS cell_cutoff,
  '${baseline_forecast}' AS baseline_forecast
FROM at_cutoff a
LEFT JOIN curve_auc c
  ON c.forecast = a.forecast AND c.lead_day = a.lead_day
LEFT JOIN cell_days_summary d
  ON d.forecast = a.forecast
ORDER BY a.forecast, a.lead_day
