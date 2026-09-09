-- Gold mart: Revenue by Customer
-- Business rules: GOLD_BUSINESS_RULES.md

CREATE OR REPLACE TABLE `ai-assesment-medillion-structure`.gold.gold_revenue_by_customer AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(*) AS total_orders,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(SUM(o.total_amount) / COUNT(*) AS DECIMAL(18, 2)) AS avg_order_value,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM `ai-assesment-medillion-structure`.silver.silver_orders o
INNER JOIN `ai-assesment-medillion-structure`.silver.silver_customers c
    ON o.customer_id = c.customer_id
WHERE o.quality_status = 'PASS'
  AND o.order_status = 'Completed'
  AND c.quality_status = 'PASS'
GROUP BY c.customer_id, c.customer_name, c.customer_segment;
