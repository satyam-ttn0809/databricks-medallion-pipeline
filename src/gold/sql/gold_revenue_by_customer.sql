-- Gold mart: Revenue by Customer
-- Business rules: GOLD_BUSINESS_RULES.md
-- Source: Silver Delta tables

CREATE OR REPLACE TABLE gold_revenue_by_customer AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(*) AS total_orders,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(SUM(o.total_amount) / COUNT(*) AS DECIMAL(18, 2)) AS avg_order_value,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM delta.`/Volumes/ai-data_assesment/data-location/silver/silver_orders` o
INNER JOIN delta.`/Volumes/ai-data_assesment/data-location/silver/silver_customers` c
    ON o.customer_id = c.customer_id
WHERE o.quality_status = 'PASS'
  AND o.order_status = 'Completed'
  AND c.quality_status = 'PASS'
GROUP BY c.customer_id, c.customer_name, c.customer_segment;
