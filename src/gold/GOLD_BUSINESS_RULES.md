# Gold Business Rules

Established from approved `design-notes.md`, `data-model.md`, and `data-quality-strategy.md` (GA-2, GA-3).

## Order Counting

- `total_orders` = `COUNT(*)` of **qualifying order rows**
- Qualifying order = `silver_orders.quality_status = 'PASS'` **AND** `order_status = 'Completed'`
- One row per completed, quality-passed order line (no deduplication beyond Silver)

## Revenue

- `total_revenue` = `SUM(total_amount)` over qualifying orders only
- Currency: source `total_amount` values (DECIMAL)
- All-time aggregation (no date filter per approved design)

## Cancelled Orders

- **Excluded** from order counts and revenue
- `order_status = 'Cancelled'` rows do not contribute to any Gold mart

## Pending Orders

- **Excluded** from order counts and revenue
- `order_status = 'Pending'` rows do not contribute to any Gold mart

## Invalid Records (Silver FAIL)

- Silver rows with `quality_status = 'FAIL'` are **excluded** from Gold joins
- FAIL rows remain in Silver for audit; not silently deleted
- Dimension tables (`silver_customers`, `silver_products`) must also be `PASS` to join

## Averages

- `avg_order_value` = `total_revenue / total_orders` (per product or per customer mart)
- Division only over qualifying orders; mart rows with zero orders are not expected when built from inner joins

## lifetime_value_actual

- Per customer: `SUM(total_amount)` of qualifying orders (= `total_revenue` for that customer)
- Not sourced from `customers.lifetime_value` column

## Customer Segmentation

- `segment_type` = `customer_segment` (Premium, Standard, Basic)
- `customer_count` = `COUNT(DISTINCT customer_id)` with at least one qualifying order
- `avg_revenue` = `AVG(customer total_revenue)` within segment
- `total_revenue` = `SUM(customer total_revenue)` within segment

## Trends Query

- **Not specified** in approved requirements, repository structure, or data model
- No trends file implemented in Phase 6 (see `ai-prompts/gold.md`)
