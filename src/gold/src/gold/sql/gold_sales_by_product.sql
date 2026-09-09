-- Gold mart: Sales by Product
-- Business rules: GOLD_BUSINESS_RULES.md

CREATE OR REPLACE TABLE `ai-assesment-medillion-structure`.gold.gold_sales_by_product AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(*) AS total_orders,
    CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(SUM(o.total_amount) / COUNT(*) AS DECIMAL(18, 2)) AS avg_order_value
FROM `ai-assesment-medillion-structure`.silver.silver_orders o
INNER JOIN `ai-assesment-medillion-structure`.silver.silver_products p
    ON o.product_id = p.product_id
WHERE o.quality_status = 'PASS'
  AND o.order_status = 'Completed'
  AND p.quality_status = 'PASS'
GROUP BY p.product_id, p.product_name, p.category;
