-- EXTERNAL:2016-2022-precip.sql
select * from md5('summary_metrics_table/2022-12-31_${grid}_lsm_${metric}_${region}_2016-01-01_${time_grouping}_${truth}_precip')
