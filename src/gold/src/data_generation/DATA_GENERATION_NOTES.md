# Data Generation Notes

## Purpose

Provide a deterministic script to generate source CSV files for the medallion pipeline with intentional quality issues defined in the project specification and approved design artifacts.

**The script has not been executed as part of Phase 3.** Data generation and validation occur when you run the script in Databricks.

## Script Location

`src/data_generation/generate_sample_data.py`

## Output Files

| File | Base Rows | Duplicate Rows | Total Rows |
|------|-----------|----------------|------------|
| `products.csv` | 500 | 0 | 500 |
| `customers.csv` | 10,000 | 10 | 10,010 |
| `orders.csv` | 100,000 | 20 | 100,020 |

## Schemas

### customers.csv

| Column | Type | Notes |
|--------|------|-------|
| customer_id | INT | PK |
| customer_name | STRING | |
| email | STRING | 50 intentional NULLs (empty field) |
| country | STRING | |
| signup_date | DATE | ISO `YYYY-MM-DD` |
| customer_segment | STRING | Premium, Standard, Basic |
| lifetime_value | DECIMAL | Two decimal places |

### orders.csv

| Column | Type | Notes |
|--------|------|-------|
| order_id | INT | PK |
| customer_id | INT | FK → customers |
| order_date | DATE | ISO `YYYY-MM-DD` |
| product_id | INT | FK → products |
| quantity | INT | |
| unit_price | DECIMAL | Two decimal places |
| total_amount | DECIMAL | Two decimal places |
| order_status | STRING | Pending, Completed, Cancelled |
| payment_date | DATE | Nullable; empty when not applicable |

### products.csv

| Column | Type | Notes |
|--------|------|-------|
| product_id | INT | PK |
| product_name | STRING | |
| category | STRING | |
| price | DECIMAL | Two decimal places |
| cost | DECIMAL | Two decimal places |
| stock_quantity | INT | |
| reorder_level | INT | |

## Relationships

- `orders.customer_id` → `customers.customer_id`
- `orders.product_id` → `products.product_id`
- Base orders reference valid customer IDs 1–10,000 and product IDs 1–500
- Invalid FK rows use IDs outside these ranges

## Intentional Data-Quality Issues

| Entity | Issue | Count | CSV Representation |
|--------|-------|-------|--------------------|
| customers | NULL email | 50 | Empty string |
| customers | Duplicate `customer_id` | 10 | Verbatim copied rows |
| orders | NULL `customer_id` | 100 | Empty string |
| orders | NULL `product_id` | 200 | Empty string |
| orders | Invalid `customer_id` FK | 50 | Integer > 10,000 |
| orders | Invalid `product_id` FK | 30 | Integer > 500 |
| orders | Duplicate `order_id` | 20 | Verbatim copied rows |

**Total explicit defect injections:** 460 rows (per requirements analysis and data-quality-strategy.md).

No intentional defects are injected into `products.csv` (per specification).

## Reproducibility

- Default seed: `42`
- Uses Python `random.Random(seed)` for all sampling
- Same script + seed + parameters should produce identical CSV content

## Output Location

Per approved design (design-notes.md, assumption A-3):

| Environment | Output Path |
|-------------|-------------|
| Local | `data/` (relative to working directory) |
| Databricks | Set `DATA_DIR` environment variable to your DBFS or Unity Catalog volume path |

The script writes three files to the configured output directory:

- `customers.csv`
- `orders.csv`
- `products.csv`

## Databricks Execution Instructions

### Option 1: Cluster job / notebook shell command

```bash
export DATA_DIR="/dbfs/FileStore/medallion-pipeline/data"
python /Workspace/Repos/<your-repo>/databricks-medallion-pipeline/src/data_generation/generate_sample_data.py \
  --output-dir "$DATA_DIR" \
  --seed 42
```

Replace `/dbfs/FileStore/medallion-pipeline/data` with your approved workspace path.

### Option 2: Databricks notebook cell

```python
import os
os.environ["DATA_DIR"] = "/dbfs/FileStore/medallion-pipeline/data"

%run /Workspace/Repos/<your-repo>/databricks-medallion-pipeline/src/data_generation/generate_sample_data
```

Or pass `--output-dir` explicitly:

```python
%run /Workspace/Repos/<your-repo>/databricks-medallion-pipeline/src/data_generation/generate_sample_data -- --output-dir /dbfs/FileStore/medallion-pipeline/data --seed 42
```

### Option 3: Skip built-in validation

```bash
python src/data_generation/generate_sample_data.py --output-dir "$DATA_DIR" --skip-validation
```

## Expected Validation Output (After You Execute)

When run without `--skip-validation`, the script prints:

1. Row counts for each generated file
2. `Validation passed: True/False`
3. `Reproducible: True/False`
4. `Details` with expected vs actual counts

### Expected counts to inspect

| Metric | Expected Value |
|--------|----------------|
| products_rows | 500 |
| customers_rows | 10,010 |
| orders_rows | 100,020 |
| null_emails | 50 |
| duplicate_customer_rows | 10 |
| null_customer_ids | 100 |
| null_product_ids | 200 |
| invalid_customer_fks | 50 |
| invalid_product_fks | 30 |
| duplicate_order_rows | 20 |

All `type_checks` in the details output should be `True`.

**Phase 3 does not record execution results.** Provide your execution output before proceeding to Phase 4.

## Out of Scope (Phase 3)

- Bronze, Silver, Gold, or Dashboard implementation
- Generated CSV files in the repository
- Claiming validation success without user execution
