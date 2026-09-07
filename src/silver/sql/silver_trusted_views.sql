-- Trusted Silver views (quality_status = PASS) for downstream Gold consumption.
-- Rejected rows remain in base Silver tables for audit (data-quality-strategy.md).

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_customers_trusted AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_customers
WHERE quality_status = 'PASS';

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_orders_trusted AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_orders
WHERE quality_status = 'PASS';

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_products_trusted AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_products
WHERE quality_status = 'PASS';

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_customers_rejected AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_customers
WHERE quality_status = 'FAIL';

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_orders_rejected AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_orders
WHERE quality_status = 'FAIL';

CREATE OR REPLACE VIEW `ai-assesment-medillion-structure`.silver.silver_products_rejected AS
SELECT *
FROM `ai-assesment-medillion-structure`.silver.silver_products
WHERE quality_status = 'FAIL';
