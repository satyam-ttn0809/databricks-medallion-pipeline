# Design Notes

## Architecture Overview

```
data/*.csv  →  Bronze (Delta)  →  Silver (Delta + DQ)  →  Gold (Delta marts)  →  Dashboard (SQL)
     ↑                                                                                      |
src/data_generation/                                                              src/dashboard/*.sql
```

| Layer | Input | Output | Technology |
|-------|-------|--------|------------|
| Source | Generated CSVs | `customers.csv`, `orders.csv`, `products.csv` | Python (Phase 3) |
| Bronze | Source CSVs | `bronze_*` Delta tables | PySpark + explicit schemas |
| Silver | Bronze tables | `silver_*` Delta tables + `silver_quality_metrics` | PySpark + shared DQ module |
| Gold | Silver tables (PASS rows, Completed orders for revenue) | Three Gold marts | PySpark |
| Dashboard | Gold marts | SQL queries + ≥3 visualizations | Databricks SQL |

---

## Layer Responsibilities

### Source (`data/`)

- Hold raw CSV files consumed by Bronze.
- Local path configured for development; Databricks reads equivalent paths on DBFS/S3 via config (resolves A-3).

### Bronze (`src/bronze/`)

- Read CSVs with explicit `StructType` schemas.
- Preserve all source values; no business transforms, deduplication, or null imputation.
- Write Delta tables with per-row metadata columns.
- Log row count per table after each ingestion run.

### Silver (`src/silver/`)

- Read Bronze Delta tables unchanged except for added quality columns.
- Apply completeness, uniqueness, referential integrity, and type/business checks.
- Flag every row `PASS` or `FAIL`; retain all rows.
- Write entity Silver tables and a metrics table with pass/fail percentages.

### Gold (`src/gold/`)

- Build three analytics marts from validated Silver data.
- Use only `quality_status = 'PASS'` dimension and fact rows.
- Revenue metrics use only `order_status = 'Completed'` orders.

### Dashboard (`src/dashboard/`)

- SQL files querying Gold marts directly (resolves A-7).
- One query file per dashboard requirement; ≥3 visualizations in Databricks SQL.

---

## Bronze Design

| Decision | Choice | Requirement |
|----------|--------|-------------|
| Read path | Config-driven: local `data/` or S3/DBFS | BR-1, A-3, NFR-6 |
| Write format | Delta, overwrite mode per entity per run | BR-4, NFR-2 |
| Schema | Explicit schemas in shared module | BR-3, NFR-4 |
| Transforms | None on business columns | BR-2 |
| Metadata columns | `_ingestion_timestamp` TIMESTAMP, `_source_file` STRING on each row | BR-5, GA-6 |
| Row count | Logged at INFO after write; not a data column | BR-5, GA-6 |
| Module | `src/bronze/ingest_raw.py` | NFR-3 |
| Tables | `bronze_customers`, `bronze_orders`, `bronze_products` | BR-4 |

**Rejected alternatives:**

- Append-only Bronze — rejected; overwrite simplifies local re-runs (EC-8) without duplicate Bronze rows.
- Separate metadata table only — rejected; per-row timestamp satisfies BR-5 audit need with simpler reads.

---

## Silver Design

| Decision | Choice | Requirement |
|----------|--------|-------------|
| Input | Bronze Delta tables | SV-1 |
| Output columns | All Bronze business columns + `quality_status` + `quality_reason` | SV-4, A-4 |
| Status values | `PASS`, `FAIL` | SV-4 |
| Reason encoding | Comma-separated failure codes | EC-1, A-5 |
| Duplicate PK rule | Flag rows where `row_number() OVER (PARTITION BY pk ORDER BY _ingestion_timestamp) > 1` | GA-5, SV-2 |
| RI reference set | Distinct PK values from Bronze parent table (includes duplicate PK values present in source) | EC-3 |
| Products checks | PK uniqueness only | GA-8, SV-2 |
| Metrics table | `silver_quality_metrics` with overall + per-check rows | SV-5, GA-7 |
| Module layout | `quality_checks.py` (shared), `validate_data.py` (orchestrator) | NFR-3, NFR-10 |

**Rejected alternatives:**

- Delete or filter FAIL rows — rejected; violates FR-7, NFR-11.
- Flag all rows sharing a duplicated PK — rejected; would over-count vs 10/20 expected duplicate records (GA-5).

---

## Gold Design

| Decision | Choice | Requirement |
|----------|--------|-------------|
| Order filter | `quality_status = 'PASS'` AND `order_status = 'Completed'` | GA-3 |
| Customer/product filter | `quality_status = 'PASS'` | GA-3 |
| Join keys | `customer_id`, `product_id` on PASS Silver entities | FR-10–FR-12 |
| `lifetime_value_actual` | `SUM(total_amount)` of Completed PASS orders per customer | GA-2 |
| `segment_type` | Maps to `customer_segment` (Premium, Standard, Basic) | A-6 |
| Aggregation grain | All-time (no date filter) | Gold spec (no date dimension specified) |
| Write format | Delta, overwrite per mart | NFR-2 |
| Module | `src/gold/build_marts.py` | NFR-3 |

**Mart outputs:**

1. `gold_sales_by_product` — grouped by product
2. `gold_revenue_by_customer` — grouped by customer
3. `gold_customer_segmentation` — grouped by `segment_type`

**Metric definitions:**

- `total_orders` — count of qualifying order rows
- `total_revenue` — sum of `total_amount`
- `avg_order_value` — `total_revenue / total_orders`

**Rejected alternatives:**

- Include Pending/Cancelled orders in revenue — rejected; revenue semantics undefined for non-completed orders (GA-3).
- Use source `lifetime_value` as `lifetime_value_actual` — rejected; "actual" implies derived from orders (GA-2).

---

## Dashboard Design

| Query | Source Mart | Purpose |
|-------|-------------|---------|
| `top_products_by_revenue.sql` | `gold_sales_by_product` | Top 10 by `total_revenue` DESC |
| `customer_revenue_distribution.sql` | `gold_revenue_by_customer` | Revenue histogram via fixed bins |
| `customer_segmentation.sql` | `gold_customer_segmentation` | Segment metrics |

**Customer revenue distribution (GA-4):** Bucket customers by `total_revenue` into fixed ranges (0–500, 501–2000, 2001–5000, 5001+) with count per bucket.

**Visualizations (≥3):** Bar chart (top products), bar/histogram (revenue distribution), bar/pie (segmentation).

---

## Configuration

Single `config/config.yaml` (NFR-6):

- Paths: `data_dir`, `bronze_dir`, `silver_dir`, `gold_dir`
- Table names per layer
- Source file names
- Spark app settings

Environment overrides via env vars for Databricks paths (no hardcoded secrets).

---

## Module Layout

```
src/
├── common/              # config loader, schemas, logging, Spark session
├── data_generation/     # Phase 3
├── bronze/              # ingest_raw.py
├── silver/              # quality_checks.py, validate_data.py
├── gold/                # build_marts.py
└── dashboard/           # *.sql
```

---

## Error-Handling Strategy

| Scenario | Behavior |
|----------|----------|
| Missing source CSV | Raise `FileNotFoundError` with configured path; log ERROR; fail pipeline (EC-7, NFR-7) |
| Missing config file | Raise `FileNotFoundError` at startup |
| Missing Bronze/Silver input path | Raise `FileNotFoundError` with layer name |
| Spark read/write failure | Log exception with table/path; re-raise |
| Empty source file | Bronze writes empty Delta table; log WARNING with row count 0 |
| All Silver rows FAIL | Silver completes; metrics show 100% fail; Gold marts may be empty; log WARNING |
| Invalid enum in source | Flag `FAIL` with reason code; do not stop pipeline |

No silent swallowing of errors. No automatic retries (orchestration out of scope).

---

## Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Unit | DQ helper functions | Pure Spark DataFrame tests with small fixtures |
| Unit | Data generation counts | Verify row counts and defect counts without Spark (Phase 3) |
| Integration | Bronze → Silver → Gold | Local Spark session; generate data → run layers sequentially |
| Validation | Known defect counts | Assert Silver metrics match 460 explicit defects (GA-1) |
| SQL | Dashboard queries | Syntax validation; run against Gold after integration |
| Manual | Databricks SQL Dashboard | Wire 3 visualizations to query results (Phase 7) |

**Validation targets (explicit defects, GA-1):** Use 460 row-level failures from requirements analysis, not ~700 approximate figure.

---

## Important Assumptions (Resolved in Phase 2)

| Phase 1 ID | Resolution |
|------------|------------|
| A-1 | Confirmed: deterministic generation in `src/data_generation/` (Phase 3) |
| A-2 | `_ingestion_timestamp` + `_source_file` per row; row count in logs |
| A-3 | `config.yaml` paths; local `data/`, Databricks via env override |
| A-4 | `quality_status` (`PASS`/`FAIL`) + `quality_reason` (codes) |
| A-5 | Any failure → `FAIL`; multiple codes concatenated |
| A-6 | `segment_type` = `customer_segment` |
| A-7 | Dashboard SQL reads Gold tables |

| Ambiguity ID | Resolution |
|--------------|------------|
| GA-1 | Validate against 460 explicit defects; treat ~700 as non-binding approximation |
| GA-2 | `lifetime_value_actual` = sum of Completed PASS order revenue per customer |
| GA-3 | Gold uses PASS Silver rows; revenue from Completed orders only |
| GA-4 | Revenue distribution = histogram buckets on `gold_revenue_by_customer.total_revenue` |
| GA-5 | Flag duplicate PK rows with row_number > 1 only |
| GA-6 | Per-row metadata columns + logged row count |
| GA-7 | Overall + per-check metrics in `silver_quality_metrics` |
| GA-8 | Products treated as clean reference; PK uniqueness check only |

---

## Design Traceability

| Requirement | Design Section |
|-------------|----------------|
| FR-1–FR-5 | Bronze Design |
| FR-6–FR-9 | Silver Design, DQ Strategy |
| FR-10–FR-12 | Gold Design |
| FR-13–FR-16 | Dashboard Design |
| NFR-1–NFR-12 | Architecture Overview, Configuration, Error Handling |
| AC-1–AC-15 | Testing Strategy, layer designs |
