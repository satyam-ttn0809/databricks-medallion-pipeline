-- Gold mart: Customer Segmentation
-- Business rules: GOLD_BUSINESS_RULES.md
-- Source: Silver Delta tables

CREATE OR REPLACE TABLE gold_customer_segmentation AS
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS customer_total_revenue
    FROM delta.`/Volumes/ai-data_assesment/data-location/silver/silver_orders` o
    INNER JOIN delta.`/Volumes/ai-data_assesment/data-location/silver/silver_customers` c
        ON o.customer_id = c.customer_id
    WHERE o.quality_status = 'PASS'
      AND o.order_status = 'Completed'
      AND c.quality_status = 'PASS'
    GROUP BY c.customer_id, c.customer_segment
)
SELECT
    customer_segment AS segment_type,
    COUNT(DISTINCT customer_id) AS customer_count,
    CAST(AVG(customer_total_revenue) AS DECIMAL(18, 2)) AS avg_revenue,
    CAST(SUM(customer_total_revenue) AS DECIMAL(18, 2)) AS total_revenue
FROM customer_revenue
GROUP BY customer_segment;
