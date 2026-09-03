# Data Model

## Entity Relationship

```
customers (1) ──< orders (M) >── (1) products
     │                │
     │                └── FK: customer_id → customers.customer_id
     │                └── FK: product_id → products.product_id
     └── PK: customer_id

products PK: product_id
orders PK: order_id
```

- **customers → orders:** one-to-many on `customer_id`
- **products → orders:** one-to-many on `product_id`
- Orders reference both dimensions; RI validated in Silver

---

## Source Schemas

### customers.csv

| Column | Type | Nullable | Constraints |
|--------|------|----------|-------------|
| customer_id | INT | No | PK |
| customer_name | STRING | No | |
| email | STRING | Yes | 50 intentional NULLs |
| country | STRING | Yes | |
| signup_date | DATE | Yes | |
| customer_segment | STRING | Yes | Premium, Standard, Basic |
| lifetime_value | DECIMAL(10,2) | Yes | |

**Volume:** 10,000 base rows + 10 duplicate PK rows = 10,010 raw rows

### orders.csv

| Column | Type | Nullable | Constraints |
|--------|------|----------|-------------|
| order_id | INT | No | PK |
| customer_id | INT | Yes | FK → customers |
| order_date | DATE | Yes | |
| product_id | INT | Yes | FK → products |
| quantity | INT | Yes | |
| unit_price | DECIMAL(10,2) | Yes | |
| total_amount | DECIMAL(10,2) | Yes | |
| order_status | STRING | Yes | Pending, Completed, Cancelled |
| payment_date | DATE | Yes | Nullable by spec |

**Volume:** 100,000 base rows + 20 duplicate PK rows = 100,020 raw rows

### products.csv

| Column | Type | Nullable | Constraints |
|--------|------|----------|-------------|
| product_id | INT | No | PK |
| product_name | STRING | Yes | |
| category | STRING | Yes | |
| price | DECIMAL(10,2) | Yes | |
| cost | DECIMAL(10,2) | Yes | |
| stock_quantity | INT | Yes | |
| reorder_level | INT | Yes | |

**Volume:** 500 rows (no intentional defects specified)

---

## Bronze Schemas

Bronze tables mirror source columns plus ingestion metadata.

### bronze_customers / bronze_orders / bronze_products

**Business columns:** Same as source schema for each entity.

**Metadata columns (all Bronze tables):**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| _ingestion_timestamp | TIMESTAMP | No | Set at ingestion time |
| _source_file | STRING | No | Source CSV path/name |

**Storage:** Delta under `database/bronze/<table_name>/`

---

## Silver Schemas

Silver tables retain all Bronze business columns plus quality columns.

**Quality columns (all Silver entity tables):**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| quality_status | STRING | No | `PASS` or `FAIL` |
| quality_reason | STRING | Yes | Comma-separated failure codes; NULL when PASS |

### silver_customers

Source/Bronze columns + quality columns.

### silver_orders

Source/Bronze columns + quality columns.

### silver_products

Source/Bronze columns + quality columns.

### silver_quality_metrics

| Column | Type | Description |
|--------|------|-------------|
| table_name | STRING | Entity name (customers, orders, products) |
| check_name | STRING | Check code or `OVERALL` |
| total_rows | BIGINT | Row count evaluated |
| passed_rows | BIGINT | Rows with PASS (overall) or rows passing individual check |
| failed_rows | BIGINT | Rows failing check |
| pass_pct | DECIMAL(5,2) | passed / total × 100 |
| fail_pct | DECIMAL(5,2) | failed / total × 100 |
| run_timestamp | TIMESTAMP | Silver run time |

**Storage:** Delta under `database/silver/<table_name>/`

---

## Gold Schemas

### gold_sales_by_product

| Column | Type | Source / Logic |
|--------|------|----------------|
| product_id | INT | silver_products.product_id |
| product_name | STRING | silver_products.product_name |
| category | STRING | silver_products.category |
| total_orders | BIGINT | COUNT of Completed PASS orders |
| total_revenue | DECIMAL(18,2) | SUM(total_amount) |
| avg_order_value | DECIMAL(18,2) | total_revenue / total_orders |

### gold_revenue_by_customer

| Column | Type | Source / Logic |
|--------|------|----------------|
| customer_id | INT | silver_customers.customer_id |
| customer_name | STRING | silver_customers.customer_name |
| customer_segment | STRING | silver_customers.customer_segment |
| total_orders | BIGINT | COUNT of Completed PASS orders |
| total_revenue | DECIMAL(18,2) | SUM(total_amount) |
| avg_order_value | DECIMAL(18,2) | total_revenue / total_orders |
| lifetime_value_actual | DECIMAL(18,2) | SUM(total_amount) — actual order revenue |

### gold_customer_segmentation

| Column | Type | Source / Logic |
|--------|------|----------------|
| segment_type | STRING | customer_segment from PASS customers |
| customer_count | BIGINT | COUNT DISTINCT customer_id with revenue activity |
| avg_revenue | DECIMAL(18,2) | AVG(customer total_revenue) within segment |
| total_revenue | DECIMAL(18,2) | SUM(customer total_revenue) within segment |

**Storage:** Delta under `database/gold/<table_name>/`

---

## Dashboard Data Sources

| Query File | Primary Gold Table |
|------------|-------------------|
| top_products_by_revenue.sql | gold_sales_by_product |
| customer_revenue_distribution.sql | gold_revenue_by_customer |
| customer_segmentation.sql | gold_customer_segmentation |

---

## Layer Lineage

```
customers.csv ──→ bronze_customers ──→ silver_customers ──┬──→ gold_revenue_by_customer
                                                          └──→ gold_customer_segmentation
orders.csv    ──→ bronze_orders    ──→ silver_orders    ──┬──→ gold_sales_by_product
                                                          ├──→ gold_revenue_by_customer
                                                          └──→ gold_customer_segmentation
products.csv  ──→ bronze_products  ──→ silver_products  ────→ gold_sales_by_product

Silver run ──→ silver_quality_metrics
```
