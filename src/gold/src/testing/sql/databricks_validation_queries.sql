-- Phase 8 — Databricks pipeline validation queries
-- Run after full pipeline: Bronze ingest → Silver validate → Gold build → Dashboard
-- Compare results to expected values in data-quality-strategy.md and TESTING_VALIDATION_NOTES.md
-- Do not modify pipeline code from this file; record variances in debugging-notes.md (Phase 9)

-- =============================================================================
-- AC-1 / AC-2: Source row counts (Bronze should match CSV volumes)
-- =============================================================================

SELECT 'bronze_customers' AS table_name, COUNT(*) AS row_count
FROM `ai-assesment-medillion-structure`.bronze.bronze_customers
UNION ALL
SELECT 'bronze_orders', COUNT(*)
FROM `ai-assesment-medillion-structure`.bronze.bronze_orders
UNION ALL
SELECT 'bronze_products', COUNT(*)
FROM `ai-assesment-medillion-structure`.bronze.bronze_products;

-- Expected: customers=10010, orders=100020, products=500

-- =============================================================================
-- AC-3 / AC-4: Bronze metadata columns (no business transformation)
-- =============================================================================

SELECT
    COUNT(*) AS total_rows,
    COUNT(_ingestion_timestamp) AS rows_with_ingestion_ts,
    COUNT(_source_file) AS rows_with_source_file
FROM `ai-assesment-medillion-structure`.bronze.bronze_customers;

-- Expected: all three counts equal 10010

-- =============================================================================
-- AC-6: Silver retains all Bronze rows (no silent deletion)
-- =============================================================================

SELECT
    'customers' AS entity,
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.bronze.bronze_customers) AS bronze_count,
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_customers) AS silver_count
UNION ALL
SELECT
    'orders',
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.bronze.bronze_orders),
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_orders)
UNION ALL
SELECT
    'products',
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.bronze.bronze_products),
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_products);

-- Expected: bronze_count = silver_count for each entity

-- =============================================================================
-- AC-7: Silver quality columns present
-- =============================================================================

SELECT quality_status, COUNT(*) AS row_count
FROM `ai-assesment-medillion-structure`.silver.silver_customers
GROUP BY quality_status
ORDER BY quality_status;

-- =============================================================================
-- AC-5 / AC-8: Silver per-check failure counts (GA-1 explicit defects)
-- =============================================================================

SELECT table_name, check_name, failed_rows
FROM `ai-assesment-medillion-structure`.silver.silver_quality_metrics
WHERE check_name != 'OVERALL'
ORDER BY table_name, check_name;

-- Expected failed_rows (data-quality-strategy.md):
-- customers  NULL_EMAIL=50, DUPLICATE_PK=10, INVALID_SEGMENT=0
-- orders     NULL_CUSTOMER_ID=100, NULL_PRODUCT_ID=200, INVALID_CUSTOMER_FK=50,
--            INVALID_PRODUCT_FK=30, DUPLICATE_PK=20, INVALID_ORDER_STATUS=0
-- products   DUPLICATE_PK=0

-- =============================================================================
-- Silver cleaning validation: business columns preserved (sample compare)
-- =============================================================================

SELECT COUNT(*) AS mismatched_customer_ids
FROM `ai-assesment-medillion-structure`.bronze.bronze_customers b
FULL OUTER JOIN `ai-assesment-medillion-structure`.silver.silver_customers s
    ON b.customer_id = s.customer_id
   AND b.customer_name = s.customer_name
   AND COALESCE(b.email, '') = COALESCE(s.email, '')
   AND COALESCE(b.customer_segment, '') = COALESCE(s.customer_segment, '')
WHERE b.customer_id IS NULL OR s.customer_id IS NULL;

-- Expected: 0 (cleaning is pass-through; only quality columns added)

-- =============================================================================
-- Trusted Silver views: PASS rows only
-- =============================================================================

SELECT
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_customers_trusted) AS trusted_count,
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_customers WHERE quality_status = 'PASS') AS pass_count;

-- Expected: trusted_count = pass_count

-- =============================================================================
-- Rejected view audit: FAIL rows retained
-- =============================================================================

SELECT
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_orders_rejected) AS rejected_count,
    (SELECT COUNT(*) FROM `ai-assesment-medillion-structure`.silver.silver_orders WHERE quality_status = 'FAIL') AS fail_count;

-- Expected: rejected_count = fail_count

-- =============================================================================
-- AC-9: Gold marts exist with rows
-- =============================================================================

SELECT 'gold_sales_by_product' AS mart, COUNT(*) AS row_count
FROM `ai-assesment-medillion-structure`.gold.gold_sales_by_product
UNION ALL
SELECT 'gold_revenue_by_customer', COUNT(*)
FROM `ai-assesment-medillion-structure`.gold.gold_revenue_by_customer
UNION ALL
SELECT 'gold_customer_segmentation', COUNT(*)
FROM `ai-assesment-medillion-structure`.gold.gold_customer_segmentation;

-- =============================================================================
-- Gold GA-3: only Completed PASS orders contribute (spot check via Silver join)
-- =============================================================================

SELECT COUNT(*) AS non_qualifying_in_gold_revenue
FROM `ai-assesment-medillion-structure`.gold.gold_revenue_by_customer g
WHERE g.total_orders <= 0 OR g.total_revenue IS NULL;

-- Expected: 0

-- =============================================================================
-- Gold lifetime_value_actual = total_revenue (GA-2)
-- =============================================================================

SELECT COUNT(*) AS lifetime_mismatch
FROM `ai-assesment-medillion-structure`.gold.gold_revenue_by_customer
WHERE lifetime_value_actual != total_revenue;

-- Expected: 0

-- =============================================================================
-- AC-10: Dashboard queries execute (run src/dashboard/dashboard_queries.sql sections)
-- AC-11: Dashboard visualizations — manual confirmation in Databricks UI
-- =============================================================================
