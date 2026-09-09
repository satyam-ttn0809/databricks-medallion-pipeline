-- Silver quality metrics summary (run after validate_all.py)

SELECT
    table_name,
    check_name,
    total_rows,
    passed_rows,
    failed_rows,
    pass_pct,
    fail_pct,
    run_timestamp
FROM `ai-assesment-medillion-structure`.silver.silver_quality_metrics
ORDER BY table_name, check_name;
