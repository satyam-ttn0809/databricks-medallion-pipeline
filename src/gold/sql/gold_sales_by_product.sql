-- Gold mart: Sales by Product
-- Business rules: GOLD_BUSINESS_RULES.md
-- Source: Silver Delta tables

CREATE OR REPLACE TABLE gold_sales_by_product AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(*) AS total_orders,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(SUM(o.total_amount) / COUNT(*) AS DECIMAL(18, 2)) AS avg_order_value
FROM delta.`/Volumes/ai-data_assesment/data-location/silver/silver_orders` o
INNER JOIN delta.`/Volumes/ai-data_assesment/data-location/silver/silver_products` p
    ON o.product_id = p.product_id
WHERE o.quality_status = 'PASS'
  AND o.order_status = 'Completed'
  AND p.quality_status = 'PASS'
GROUP BY p.product_id, p.product_name, p.category;
