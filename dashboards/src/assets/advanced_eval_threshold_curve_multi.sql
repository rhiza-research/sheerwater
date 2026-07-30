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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
      AND (forecast IN (${forecast_option}) OR forecast = '${eval_forecast}' OR forecast = '${baseline_forecast}')
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
valid_cells AS (
  -- Null percent_good cells produce empty/zero curves; exclude them.
  SELECT *
  FROM cell_avgs
  WHERE percent_good_avg IS NOT NULL
),
per_forecast AS (
  SELECT
    t.cell_threshold,
    c.lead_day,
    c.forecast,
    COUNT(*) FILTER (WHERE c.percent_good_avg >= t.cell_threshold) AS good_cells,
    COUNT(*) AS points_total
  FROM thresholds t
  CROSS JOIN valid_cells c
  GROUP BY t.cell_threshold, c.lead_day, c.forecast
  HAVING COUNT(*) > 0
)
SELECT
  cell_threshold,
  lead_day,
  forecast,
  good_cells::double precision AS good_cells,
  points_total::double precision AS points_total,
  '${informative_cutoff}'::double precision AS informative_cutoff,
  '${actionable_cutoff}'::double precision AS actionable_cutoff,
  -- Forces panel refresh when Eval/Baseline forecast changes; also read by Plotly script.
  '${eval_forecast}' AS eval_forecast,
  '${baseline_forecast}' AS baseline_forecast
FROM per_forecast
ORDER BY forecast, lead_day, cell_threshold
