# Silver Validation Notes

## Unity Catalog Targets

| Table | Full name |
|-------|-----------|
| silver_customers | `` `ai-assesment-medillion-structure`.`silver`.`silver_customers` `` |
| silver_orders | `` `ai-assesment-medillion-structure`.`silver`.`silver_orders` `` |
| silver_products | `` `ai-assesment-medillion-structure`.`silver`.`silver_products` `` |
| silver_quality_metrics | `` `ai-assesment-medillion-structure`.`silver`.`silver_quality_metrics` `` |

**Bronze inputs** (read via `spark.table`):

`` `ai-assesment-medillion-structure`.`bronze`.`bronze_*` ``

## Prerequisite

```sql
CREATE SCHEMA IF NOT EXISTS `ai-assesment-medillion-structure`.silver;
```

Bronze tables must exist before Silver runs.

## Databricks Job Tasks

### Option A — Single task (recommended for metrics)

Run `validate_all.py` or `validate_data.py` to write all Silver tables and `silver_quality_metrics`.

### Option B — Three entity tasks (mirrors Bronze)

1. `01_validate_customers.py`
2. `03_validate_products.py` (run before orders; products are clean reference data)
3. `02_validate_orders.py` (requires bronze_customers + bronze_products for RI)

Then run `validate_all.py` once to refresh `silver_quality_metrics`, **or** query Silver tables directly.

## Validation Categories

| Category | Customers | Orders | Products |
|----------|-----------|--------|----------|
| Completeness | NULL_EMAIL | NULL_CUSTOMER_ID, NULL_PRODUCT_ID | — |
| Uniqueness | DUPLICATE_PK | DUPLICATE_PK | DUPLICATE_PK |
| Referential integrity | — | INVALID_CUSTOMER_FK, INVALID_PRODUCT_FK | — |
| Type/business | INVALID_SEGMENT | INVALID_ORDER_STATUS | — |

## Expected Defect Counts (Phase 3 intentional issues)

| Check | Expected failures |
|-------|-------------------|
| NULL_EMAIL | 50 |
| DUPLICATE_PK (customers) | 10 |
| NULL_CUSTOMER_ID | 100 |
| NULL_PRODUCT_ID | 200 |
| INVALID_CUSTOMER_FK | 50 |
| INVALID_PRODUCT_FK | 30 |
| DUPLICATE_PK (orders) | 20 |

Inspect after run:

```sql
SELECT * FROM `ai-assesment-medillion-structure`.silver.silver_quality_metrics
ORDER BY table_name, check_name;
```

## Behaviour

- All Bronze rows are retained in Silver
- `quality_status`: `PASS` or `FAIL`
- `quality_reason`: comma-separated failure codes (NULL when PASS)
- FAIL rows are **not** deleted
