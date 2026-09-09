-- Dashboard queries — Phase 7
-- Sources: design-notes.md (Dashboard Design), data-model.md (Dashboard Data Sources)
-- All queries read approved Gold marts only (no Silver/Bronze access).

-- =============================================================================
-- 1. Top 10 products by revenue (DB-1 / FR-13)
-- Source mart: gold_sales_by_product
-- =============================================================================

SELECT
    product_id,
    product_name,
    category,
    total_orders,
    total_revenue,
    avg_order_value
FROM `ai-assesment-medillion-structure`.gold.gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;

-- =============================================================================
-- 2. Customer revenue distribution (DB-2 / FR-14, GA-4)
-- Source mart: gold_revenue_by_customer
-- Buckets: 0–500, 501–2000, 2001–5000, 5001+ (design-notes.md)
-- =============================================================================

SELECT
    revenue_bucket,
    customer_count
FROM (
    SELECT
        CASE
            WHEN total_revenue <= 500 THEN '0-500'
            WHEN total_revenue <= 2000 THEN '501-2000'
            WHEN total_revenue <= 5000 THEN '2001-5000'
            ELSE '5001+'
        END AS revenue_bucket,
        CASE
            WHEN total_revenue <= 500 THEN 1
            WHEN total_revenue <= 2000 THEN 2
            WHEN total_revenue <= 5000 THEN 3
            ELSE 4
        END AS bucket_sort_order,
        COUNT(*) AS customer_count
    FROM `ai-assesment-medillion-structure`.gold.gold_revenue_by_customer
    GROUP BY
        CASE
            WHEN total_revenue <= 500 THEN '0-500'
            WHEN total_revenue <= 2000 THEN '501-2000'
            WHEN total_revenue <= 5000 THEN '2001-5000'
            ELSE '5001+'
        END,
        CASE
            WHEN total_revenue <= 500 THEN 1
            WHEN total_revenue <= 2000 THEN 2
            WHEN total_revenue <= 5000 THEN 3
            ELSE 4
        END
) bucketed
ORDER BY bucket_sort_order;

-- =============================================================================
-- 3. Customer segmentation (DB-3 / FR-15)
-- Source mart: gold_customer_segmentation
-- =============================================================================

SELECT
    segment_type,
    customer_count,
    avg_revenue,
    total_revenue
FROM `ai-assesment-medillion-structure`.gold.gold_customer_segmentation
ORDER BY segment_type;
