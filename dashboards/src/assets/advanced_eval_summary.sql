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
      AND $region = '__REGION_OPTION__'
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
      AND $region = '__REGION_OPTION__'
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
      AND $region = '__REGION_OPTION__'
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
      AND $region = '__REGION_OPTION__'
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
      AND $region = '__REGION_OPTION__'
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
      AND $region = '__REGION_OPTION__'
      AND lead_day IN (7, 14, 21, 28, 35, 42)
      AND '${source}' IN ('forecast', 'both')
    GROUP BY forecast, $region, lead_day, lat, lon
  ) combined
  GROUP BY forecast, $region, lead_day, lat, lon
)
SELECT
  forecast,
  $region,
  lead_day,
      COUNT(CASE WHEN percent_good_avg > ${threshold}::float THEN 1 END) AS points_above_threshold,
  COUNT(percent_good_avg) AS points_total,
  AVG(metric_avg) AS metric_mean,
  AVG(percent_good_avg) AS percent_good_mean,
  AVG(percent_good_members_avg) AS percent_good_members_mean,
  AVG(event_count_avg) AS event_count_mean,
  -- forces panel refresh when View changes; also read by Plotly scripts
  '${table_view}' AS table_view,
  '${compare_regions}' AS compare_regions,
  '${prob_type}' AS prob_type
FROM cell_avgs
GROUP BY forecast, $region, lead_day
ORDER BY forecast, $region, lead_day
