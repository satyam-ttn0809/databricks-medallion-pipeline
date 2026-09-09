# Gold Layer Implementation Notes

## Phase Gate

Phases 0–5: APPROVED (`PROJECT_STATUS.md`)

## Gold Inputs (Silver only — no Bronze)

| Silver table | Used by |
|--------------|---------|
| `silver_orders` | All three marts |
| `silver_customers` | Revenue by Customer, Customer Segmentation |
| `silver_products` | Sales by Product |

Unity Catalog: `` `ai-assesment-medillion-structure`.`silver`.`<table>` ``

## Approved Gold Inclusion Rule (GA-3)

Gold reads Silver tables and applies **documented business filters only**:

- `quality_status = 'PASS'` on Silver entities (approved in data-quality-strategy.md)
- `order_status = 'Completed'` for revenue/order metrics (approved in design-notes.md)

This is **not** Silver cleaning — it is the approved Gold consumption rule for trusted analytics rows.

## Gold Datasets Created

| Table | Spec name | Columns |
|-------|-----------|---------|
| `gold_sales_by_product` | Sales by Product | product_id, product_name, category, total_orders, total_revenue, avg_order_value |
| `gold_revenue_by_customer` | Revenue by Customer | customer_id, customer_name, customer_segment, total_orders, total_revenue, avg_order_value, lifetime_value_actual |
| `gold_customer_segmentation` | Customer Segmentation | segment_type, customer_count, avg_revenue, total_revenue |

Unity Catalog: `` `ai-assesment-medillion-structure`.`gold`.`<table>` ``

## Transformations (approved only)

1. **Sales by Product** — join qualifying orders to PASS products; group by product; count orders; sum revenue; avg = revenue/orders
2. **Revenue by Customer** — join qualifying orders to PASS customers; group by customer; count/sum/avg; lifetime_value_actual = total_revenue
3. **Customer Segmentation** — aggregate customer revenue by segment_type (= customer_segment); count distinct customers; avg/sum revenue

## Silver Boundary (not implemented in Gold)

- No NULL imputation
- No duplicate removal
- No FK repair
- No DQ flagging
- No Silver validation logic

## Implementation Files

| File | Purpose |
|------|---------|
| `gold_common.py` | UC Silver read / Gold write |
| `build_marts.py` | PySpark mart build + schema validators |
| `sql/*.sql` | Equivalent SQL mart definitions |
| `GOLD_BUSINESS_RULES.md` | Approved metric rules |

## Databricks Execution

```sql
CREATE SCHEMA IF NOT EXISTS `ai-assesment-medillion-structure`.gold;
```

Run: `build_marts.py` (or execute `sql/*.sql` individually)

## Validation (implementation review only)

- Three marts match data-model.md schemas
- Calculations match GOLD_BUSINESS_RULES.md
- Reads Silver only via `read_silver()` / `spark.table()`
- No undocumented columns or marts
- Runtime execution not performed by LLM — user must run in Databricks
