# Requirements Analysis

## Problem Statement

Build an evaluation-scoped, production-style e-commerce analytics pipeline on Databricks using the medallion architecture:

**Source CSVs → Bronze → Silver → Gold → Databricks SQL Dashboard**

The project must demonstrate requirement analysis, architecture/design, Python/PySpark/SQL implementation, data quality validation, testing, debugging, documentation, and responsible AI usage. The solution must prioritize correctness, maintainability, testability, and clear engineering decisions without over-engineering.

---

## Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | Ingest three source CSV files (`customers.csv`, `orders.csv`, `products.csv`) into Bronze layer | Spec: Source Data, Bronze |
| FR-2 | Preserve source data in Bronze without business transformations | Spec: Bronze |
| FR-3 | Apply explicit schemas during Bronze ingestion where practical | Spec: Bronze, Engineering Standards |
| FR-4 | Persist Bronze tables | Spec: Bronze |
| FR-5 | Record Bronze ingestion metadata including row count and ingestion timestamp | Spec: Bronze |
| FR-6 | Implement Silver-layer data quality validation | Spec: Silver |
| FR-7 | Flag bad records in Silver; do not silently delete them | Spec: Silver, Engineering Standards |
| FR-8 | Include a quality result/status column on Silver outputs | Spec: Silver |
| FR-9 | Produce quality metrics showing passed/failed percentages | Spec: Silver |
| FR-10 | Build Gold mart: Sales by Product with specified columns | Spec: Gold |
| FR-11 | Build Gold mart: Revenue by Customer with specified columns | Spec: Gold |
| FR-12 | Build Gold mart: Customer Segmentation with specified columns | Spec: Gold |
| FR-13 | Create SQL queries for Top 10 products by revenue | Spec: Dashboard |
| FR-14 | Create SQL queries for Customer revenue distribution | Spec: Dashboard |
| FR-15 | Create SQL queries for Customer segmentation | Spec: Dashboard |
| FR-16 | Dashboard must include at least 3 visualizations | Spec: Dashboard |
| FR-17 | Source data must include specified intentional quality issues for validation | Spec: Source Data |
| FR-18 | Project must include evidence of requirement understanding, design decisions, validation, testing, debugging, documentation, reflection, and AI usage | Spec: Important |

---

## Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-1 | Use Python, PySpark, and SQL | Spec: Engineering Standards |
| NFR-2 | Use Delta where appropriate | Spec: Engineering Standards |
| NFR-3 | Modular code structure under `src/` | Spec: Repository Structure, Engineering Standards |
| NFR-4 | Explicit schemas | Spec: Engineering Standards |
| NFR-5 | Meaningful logging | Spec: Engineering Standards |
| NFR-6 | Configuration instead of hardcoded environment-specific values | Spec: Engineering Standards |
| NFR-7 | Clear error handling | Spec: Engineering Standards |
| NFR-8 | Deterministic/reproducible test data where practical | Spec: Engineering Standards |
| NFR-9 | No hardcoded secrets or credentials | Spec: Engineering Standards |
| NFR-10 | Avoid unnecessary frameworks, abstractions, duplicate logic, and overly complex orchestration | Spec: Engineering Standards |
| NFR-11 | Do not silently drop bad data | Spec: Engineering Standards |
| NFR-12 | Do not invent requirements beyond the specification | Spec: AI Working Rules |

---

## Source Data Requirements

### customers.csv

| Attribute | Requirement |
|-----------|-------------|
| Row count | 10,000 base rows |
| customer_id | INT, primary key |
| customer_name | STRING |
| email | STRING |
| country | STRING |
| signup_date | DATE |
| customer_segment | STRING; values: Premium, Standard, Basic |
| lifetime_value | DECIMAL |
| Intentional issues | 50 NULL emails; 10 duplicate `customer_id` records |

### orders.csv

| Attribute | Requirement |
|-----------|-------------|
| Row count | 100,000 base rows |
| order_id | INT, primary key |
| customer_id | INT, FK → customers |
| order_date | DATE |
| product_id | INT, FK → products |
| quantity | INT |
| unit_price | DECIMAL |
| total_amount | DECIMAL |
| order_status | STRING; values: Pending, Completed, Cancelled |
| payment_date | DATE, nullable |
| Intentional issues | 100 NULL `customer_id`; 200 NULL `product_id`; 50 invalid `customer_id` references; 30 invalid `product_id` references; 20 duplicate `order_id` records |

### products.csv

| Attribute | Requirement |
|-----------|-------------|
| Row count | 500 rows |
| product_id | INT, primary key |
| product_name | STRING |
| category | STRING |
| price | DECIMAL |
| cost | DECIMAL |
| stock_quantity | INT |
| reorder_level | INT |
| Intentional issues | **Not specified** for products |

### Overall source data note

The specification states that approximately 700 problematic rows are expected. The explicitly listed intentional issues total **460 rows** (60 customers + 400 orders). This discrepancy is recorded under **Genuine Ambiguities**.

---

## Bronze Requirements

| ID | Requirement |
|----|-------------|
| BR-1 | Read raw CSVs from S3/DBFS |
| BR-2 | Preserve source values without business transformations (including NULLs and duplicates) |
| BR-3 | Apply explicit schemas where practical |
| BR-4 | Persist Bronze tables |
| BR-5 | Record ingestion metadata: row count and ingestion timestamp |

**Not specified in Bronze requirements:**

- Exact Bronze table naming convention
- Append vs overwrite ingestion mode
- Whether ingestion metadata is stored as table columns, audit log, or separate metadata record
- Local development path when not using S3/DBFS

---

## Silver Requirements

| ID | Requirement |
|----|-------------|
| SV-1 | Implement data quality validation |
| SV-2 | Required check categories: (1) Completeness, (2) Uniqueness, (3) Referential integrity, (4) Type/business validation as appropriate |
| SV-3 | Bad records must be flagged, not silently deleted |
| SV-4 | Include a quality result/status column |
| SV-5 | Produce quality metrics with passed/failed percentages |

**Expected Silver validation scope (derived from source intentional issues):**

| Entity | Check Type | Known Defect Count |
|--------|------------|-------------------|
| customers | Completeness (NULL email) | 50 |
| customers | Uniqueness (duplicate PK) | 10 |
| orders | Completeness (NULL customer_id) | 100 |
| orders | Completeness (NULL product_id) | 200 |
| orders | Referential integrity (invalid customer_id) | 50 |
| orders | Referential integrity (invalid product_id) | 30 |
| orders | Uniqueness (duplicate PK) | 20 |

**Not specified in Silver requirements:**

- Exact column names for quality status/reason fields
- Whether all duplicate rows are flagged or only excess occurrences
- Per-check vs per-table metrics schema
- Whether products require any Silver checks beyond type/business validation as appropriate

---

## Data Quality Requirements

| Category | Requirement | Applies To |
|----------|-------------|------------|
| Completeness | Detect NULL/missing required values | customers (email), orders (customer_id, product_id) |
| Uniqueness | Detect duplicate primary keys | customers (customer_id), orders (order_id) |
| Referential integrity | Detect FK values not present in parent entity | orders → customers, orders → products |
| Type/business validation | Validate enums and business rules as appropriate | customer_segment, order_status; other rules not explicitly listed |

**Mandatory behavior:**

- Flag failures; do not silently delete invalid records
- Expose quality status on Silver outputs
- Report pass/fail percentages via quality metrics

**Not specified:**

- Exact failure reason encoding (single code vs concatenated codes)
- Handling of rows with multiple simultaneous failures
- Whether Silver retains all Bronze columns unchanged
- Explicit validation rules for `total_amount`, `payment_date`, or product price/cost relationships

---

## Gold Requirements

### 1. Sales by Product

| Column | Required |
|--------|----------|
| product_id | Yes |
| product_name | Yes |
| category | Yes |
| total_orders | Yes |
| total_revenue | Yes |
| avg_order_value | Yes |

### 2. Revenue by Customer

| Column | Required |
|--------|----------|
| customer_id | Yes |
| customer_name | Yes |
| customer_segment | Yes |
| total_orders | Yes |
| total_revenue | Yes |
| avg_order_value | Yes |
| lifetime_value_actual | Yes |

### 3. Customer Segmentation

| Column | Required |
|--------|----------|
| segment_type | Yes |
| customer_count | Yes |
| avg_revenue | Yes |
| total_revenue | Yes |

**Not specified in Gold requirements:**

- Whether Gold uses only Silver records with passing quality status
- Whether revenue metrics include all order statuses or only Completed orders
- Definition/calculation of `lifetime_value_actual`
- Whether `segment_type` maps directly to `customer_segment` source values
- Aggregation grain (e.g., all-time vs date-filtered)
- Join logic when dimension or fact records fail Silver checks

---

## Dashboard Requirements

| ID | Requirement |
|----|-------------|
| DB-1 | SQL query: Top 10 products by revenue |
| DB-2 | SQL query: Customer revenue distribution |
| DB-3 | SQL query: Customer segmentation |
| DB-4 | At least 3 visualizations total |

**Not specified:**

- Dashboard platform details beyond Databricks SQL
- Visualization types (bar, pie, histogram, etc.)
- Definition of "customer revenue distribution" (bins, percentiles, segments, etc.)
- Sort order tie-breaking for Top 10 products
- Whether dashboard reads Gold tables directly

---

## Acceptance Criteria

| ID | Criterion | Verification Basis |
|----|-----------|-------------------|
| AC-1 | Three source CSV files exist with specified schemas and base row counts | Source Data spec |
| AC-2 | Intentional source defects match specified counts | Source Data spec |
| AC-3 | Bronze tables persist raw source data with explicit schemas | Bronze spec |
| AC-4 | Bronze ingestion records row count and ingestion timestamp | Bronze spec |
| AC-5 | Silver applies completeness, uniqueness, referential integrity, and appropriate type/business checks | Silver spec |
| AC-6 | Silver flags bad records; none silently deleted | Silver spec |
| AC-7 | Silver outputs include quality status column | Silver spec |
| AC-8 | Silver quality metrics report pass/fail percentages | Silver spec |
| AC-9 | Three Gold marts exist with required columns | Gold spec |
| AC-10 | Three dashboard SQL query areas exist (Top 10 products, revenue distribution, segmentation) | Dashboard spec |
| AC-11 | Dashboard includes ≥3 visualizations | Dashboard spec |
| AC-12 | Implementation uses Python, PySpark, SQL, Delta where appropriate | Engineering Standards |
| AC-13 | Code is modular, configurable, logged, and handles errors clearly | Engineering Standards |
| AC-14 | No hardcoded secrets | Engineering Standards |
| AC-15 | Project artifacts demonstrate analysis, design, testing, debugging, documentation, and AI evidence | Important section |

---

## Assumptions

> Applied using **ASSUMPTION → DOCUMENT → CONTINUE**. These are not blocking for Phase 1; they require confirmation in Phase 2 (Architecture) or later implementation phases.

| ID | Assumption | Rationale | Phase to Resolve |
|----|------------|-----------|------------------|
| A-1 | Source CSV files will be produced deterministically to satisfy FR-17 and NFR-8, using the `src/data_generation/` module path from repository structure | Spec requires intentional defects and reproducible test data; no external CSV supply mechanism is specified | Phase 3 |
| A-2 | Bronze ingestion metadata (`row count`, `ingestion timestamp`) will be captured at ingestion time via logging and/or metadata fields; exact storage mechanism deferred to architecture | Spec names both metadata elements but not their storage form | Phase 2 |
| A-3 | Local development may read CSVs from `data/` via configuration, while Databricks deployment reads from S3/DBFS as specified | Spec names S3/DBFS; local path not specified; NFR-6 requires configuration | Phase 2 |
| A-4 | Silver quality status column will use a pass/fail (or equivalent) indicator; optional reason detail may be added if needed for debugging | Spec requires quality result/status column; reason field not mandated | Phase 2 |
| A-5 | All rows failing any required check receive a failed quality status; rows may accumulate multiple failure types | Spec requires flagging, not deletion; multi-failure handling not specified | Phase 2 |
| A-6 | `segment_type` in Gold Customer Segmentation corresponds to source `customer_segment` values (Premium, Standard, Basic) | Column name differs; semantic mapping strongly implied | Phase 2 |
| A-7 | Dashboard SQL queries will target Gold-layer outputs | Pipeline ends at Gold → Dashboard; query sources not explicitly named | Phase 2 |

---

## Edge Cases

| ID | Edge Case | Expected Handling (per spec constraints) |
|----|-----------|------------------------------------------|
| EC-1 | Row has multiple quality failures (e.g., NULL customer_id and invalid customer_id) | Must be flagged, not deleted; all applicable failures should be detectable |
| EC-2 | Duplicate PK rows (customers/orders) | Must be flagged via uniqueness check; records must not be silently removed |
| EC-3 | Order references customer/product IDs that exist only among failing duplicate customer rows | Referential integrity behavior depends on whether valid PK set excludes duplicates; not specified |
| EC-4 | Orders with Cancelled or Pending status | Included in source; impact on Gold revenue metrics not specified |
| EC-5 | NULL payment_date on Completed orders (or non-Completed orders) | Nullable by schema; no explicit validation rule specified |
| EC-6 | All rows in an entity fail quality checks | Pipeline must still flag and report metrics; Gold population behavior not specified |
| EC-7 | Empty or missing source CSV at ingestion | Spec requires clear error handling (NFR-7); exact error type not specified |
| EC-8 | Re-running Bronze ingestion | Idempotency/append behavior not specified |
| EC-9 | Invalid enum values for customer_segment or order_status if introduced in source | Covered by "type/business validation as appropriate" if present in data |
| EC-10 | products.csv has no listed intentional defects | Silver may still apply uniqueness/type checks; ~700 problematic rows claim may not apply to products |

---

## Genuine Ambiguities

These items are **not defined** in the specification and **materially affect** design or validation. They are documented here; resolution is deferred to Phase 2 unless otherwise instructed.

| ID | Ambiguity | Why It Matters | Possible Interpretations |
|----|-----------|----------------|--------------------------|
| GA-1 | **~700 problematic rows** vs **460 explicitly listed defects** | Affects validation thresholds and test expectations | (a) ~700 is approximate across pipeline including downstream duplicates/effects; (b) additional undocumented defects expected; (c) specification arithmetic inconsistency |
| GA-2 | **Definition of `lifetime_value_actual`** in Gold Revenue by Customer | Required output column with no calculation rule | (a) Sum of Completed order revenue; (b) Sum of all order revenue; (c) Copy/compare to source `lifetime_value`; (d) Other derived metric |
| GA-3 | **Gold revenue inclusion rules** — which orders and which Silver rows count | Determines mart values and dashboard results | (a) All orders regardless of status; (b) Completed orders only; (c) PASS Silver rows only; (d) PASS + Completed combined |
| GA-4 | **Customer revenue distribution** dashboard query | Required visualization input with no distribution definition | (a) Histogram of customer total revenue; (b) Revenue by segment; (c) Percentile bands; (d) Top-N vs long tail |
| GA-5 | **Duplicate row handling in Silver** — flag all duplicates or only extras | Affects fail counts (10 customer dupes could be 10 or 20 failed rows) | (a) Flag every row sharing a duplicated PK; (b) Flag only non-first occurrences |
| GA-6 | **Bronze metadata storage format** | Affects table schema and auditability | (a) Per-row `_ingestion_timestamp` column; (b) Run-level log only; (c) Separate metadata table |
| GA-7 | **Quality metrics granularity** | Affects metrics table design and validation | (a) One overall pass/fail per entity; (b) Per-check metrics; (c) Both |
| GA-8 | **products.csv quality scope** | No intentional defects listed; unclear if products contribute to ~700 figure | (a) Products are clean reference data; (b) Undocumented product defects expected |

**Blocking status for Phase 1:** None of the above block completion of requirement analysis. They must be resolved in Phase 2 (Architecture & Data Model) before implementation.

---

## Out of Scope (Not in Specification)

- Real-time/streaming ingestion
- Production CI/CD to Databricks
- Authentication/secret management beyond secure configuration practices
- ML or analytics beyond the three specified Gold marts
- Orchestration platform selection (Airflow, Databricks Jobs, etc.)

---

## Traceability Summary

| Specification Section | Covered In |
|-----------------------|------------|
| Objective | Problem Statement, FR-1–FR-18 |
| Source Data | Source Data Requirements, Edge Cases |
| Bronze | Bronze Requirements |
| Silver | Silver Requirements, Data Quality Requirements |
| Gold | Gold Requirements |
| Dashboard | Dashboard Requirements |
| Engineering Standards | Non-Functional Requirements |
| Important (evaluation criteria) | FR-18, Acceptance Criteria |
| Repository Structure | NFR-3 (modular layout reference only; no architecture design in this document) |
