--EXTERNAL:station_codes.sql
SELECT 
  code || ' - ' || location_name AS code_location
FROM 
  ${tahmo_deployment_name};
