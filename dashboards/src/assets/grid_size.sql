--EXTERNAL:grid_size.sql
SELECT
  CASE '${grid}'
    WHEN 'global0_25'  THEN 0.25/2 + 1e-6
    WHEN 'global1_5'   THEN 1.5/2  + 1e-6
    WHEN 'global0_1'     THEN 0.1/2  + 1e-6
    WHEN 'global0_05'     THEN 0.05/2  + 1e-6
  END AS grid_size
