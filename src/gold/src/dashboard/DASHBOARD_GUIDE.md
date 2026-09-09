# Dashboard Guide — Phase 7

## Phase Gate

- Phases 0–6: APPROVED (`PROJECT_STATUS.md`)
- Dashboard reads **Gold marts only** — no Silver cleaning, DQ correction, or validation in dashboard SQL (A-7, design-notes.md)

## Gold Data Sources

| Dashboard item | Gold table | Full Unity Catalog name |
|----------------|------------|-------------------------|
| Top 10 products by revenue | `gold_sales_by_product` | `` `ai-assesment-medillion-structure`.`gold`.`gold_sales_by_product` `` |
| Customer revenue distribution | `gold_revenue_by_customer` | `` `ai-assesment-medillion-structure`.`gold`.`gold_revenue_by_customer` `` |
| Customer segmentation | `gold_customer_segmentation` | `` `ai-assesment-medillion-structure`.`gold`.`gold_customer_segmentation` `` |

**Prerequisite:** Gold tables must exist (run `build_marts.py` in Databricks before dashboard queries).

## Query File

All three dashboard queries are in `dashboard_queries.sql`.

---

## 1. Top 10 Products by Revenue (DB-1 / FR-13)

**Source:** `gold_sales_by_product`

**Logic (approved):** Select products ordered by `total_revenue` DESC; limit 10 rows (design-notes.md).

**Columns used:** `product_id`, `product_name`, `category`, `total_orders`, `total_revenue`, `avg_order_value`

### Visualization guidance

| Setting | Value |
|---------|-------|
| Chart type | **Bar chart** (design-notes.md) |
| X-axis | `product_name` (or `product_id` if names overlap) |
| Y-axis | `total_revenue` |
| Sort | Descending by `total_revenue` (query pre-sorts) |
| Title | Top 10 Products by Revenue |

**Databricks SQL Dashboard:** Create a visualization from the Top 10 query; use bar chart with product on category axis and revenue on value axis.

---

## 2. Customer Revenue Distribution (DB-2 / FR-14, GA-4)

**Source:** `gold_revenue_by_customer`

**Logic (approved GA-4):** Bucket each customer's `total_revenue` into fixed ranges and count customers per bucket:

| Bucket | `total_revenue` range |
|--------|------------------------|
| `0-500` | ≤ 500 |
| `501-2000` | > 500 and ≤ 2000 |
| `2001-5000` | > 2000 and ≤ 5000 |
| `5001+` | > 5000 |

**Output columns:** `revenue_bucket`, `customer_count`

### Visualization guidance

| Setting | Value |
|---------|-------|
| Chart type | **Bar chart** or **histogram** (design-notes.md) |
| X-axis | `revenue_bucket` (ordered low → high) |
| Y-axis | `customer_count` |
| Title | Customer Revenue Distribution |

**Databricks SQL Dashboard:** Use bar chart; ensure bucket order is 0-500 → 5001+ (query includes `bucket_sort_order` for ordering).

---

## 3. Customer Segmentation (DB-3 / FR-15)

**Source:** `gold_customer_segmentation`

**Logic (approved):** Read pre-aggregated segment metrics from Gold mart (`segment_type`, `customer_count`, `avg_revenue`, `total_revenue`).

**Note:** `segment_type` = `customer_segment` per approved design (A-6). No additional segmentation logic in dashboard.

### Visualization guidance

| Setting | Value |
|---------|-------|
| Chart type | **Bar chart** or **pie chart** (design-notes.md) |
| Category / slice | `segment_type` |
| Value options | `customer_count` (share of customers) or `total_revenue` (share of revenue) |
| Title | Customer Segmentation |

**Suggested pairings:**

- **Bar chart:** X = `segment_type`, Y = `total_revenue` or `customer_count`
- **Pie chart:** Slice = `segment_type`, Value = `customer_count` or `total_revenue`

---

## Databricks SQL Dashboard Setup

1. Open **SQL** → **Dashboards** in Databricks workspace.
2. Create a new dashboard (≥3 visualizations required per DB-4 / FR-16).
3. Add three queries from `dashboard_queries.sql` (one per section).
4. Wire visualizations per guidance above:
   - Visualization 1: Top 10 products — bar chart
   - Visualization 2: Customer revenue distribution — bar/histogram
   - Visualization 3: Customer segmentation — bar or pie chart

## Boundaries (not in dashboard scope)

- No reads from Silver or Bronze tables
- No `quality_status` filtering (Gold marts already apply GA-3)
- No new metrics, bins, or business rules beyond approved artifacts
- No data cleaning or DQ correction

## Validation Status

SQL reviewed against approved Gold schemas (`data-model.md`) and dashboard design (`design-notes.md`). **Runtime execution in Databricks not performed by implementation agent** — user must run queries against populated Gold tables and confirm results before marking Phase 7 APPROVED.
