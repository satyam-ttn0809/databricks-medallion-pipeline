# Data Quality Strategy

## Principles

1. **Detect, flag, report** — never silently delete (FR-7, NFR-11)
2. **Explicit failure codes** — auditable `quality_reason` values
3. **Measurable metrics** — pass/fail percentages per entity and per check (FR-9)
4. **Deterministic** — same Bronze input yields same flags (NFR-8)

---

## Check Matrix

### customers (silver_customers)

| Category | Check | Code | Expected Failures |
|----------|-------|------|-------------------|
| Completeness | email IS NOT NULL AND email != '' | `NULL_EMAIL` | 50 |
| Uniqueness | customer_id unique (row_number > 1 flagged) | `DUPLICATE_PK` | 10 |
| Business | customer_segment IN (Premium, Standard, Basic) | `INVALID_SEGMENT` | 0 (generated clean) |

### orders (silver_orders)

| Category | Check | Code | Expected Failures |
|----------|-------|------|-------------------|
| Completeness | customer_id IS NOT NULL | `NULL_CUSTOMER_ID` | 100 |
| Completeness | product_id IS NOT NULL | `NULL_PRODUCT_ID` | 200 |
| Referential integrity | customer_id exists in bronze_customers.customer_id | `INVALID_CUSTOMER_FK` | 50 |
| Referential integrity | product_id exists in bronze_products.product_id | `INVALID_PRODUCT_FK` | 30 |
| Uniqueness | order_id unique (row_number > 1 flagged) | `DUPLICATE_PK` | 20 |
| Business | order_status IN (Pending, Completed, Cancelled) | `INVALID_ORDER_STATUS` | 0 (generated clean) |

### products (silver_products)

| Category | Check | Code | Expected Failures |
|----------|-------|------|-------------------|
| Uniqueness | product_id unique | `DUPLICATE_PK` | 0 |

**Not implemented (not required by spec):**

- `total_amount = quantity × unit_price` validation
- `payment_date` required for Completed orders
- `price >= cost` on products

---

## Duplicate PK Rule (GA-5)

Use window function ordered by `_ingestion_timestamp`:

- `row_number() OVER (PARTITION BY pk ORDER BY _ingestion_timestamp) = 1` → eligible for PASS on uniqueness
- `row_number > 1` → `DUPLICATE_PK`

Expected failures: 10 (customers), 20 (orders) — matches intentional duplicate record counts.

---

## Referential Integrity Rule (EC-3)

- Build valid FK sets from **all distinct PK values** in Bronze parent tables.
- Duplicate customer PK values in Bronze are included in the valid set.
- Orders with NULL FK fail completeness before RI; invalid non-null FKs fail RI.

---

## Multi-Failure Handling (EC-1, A-5)

- Evaluate all applicable checks per row.
- Accumulate all failure codes into `quality_reason` (comma-separated, sorted alphabetically).
- `quality_status = FAIL` if any check fails; `PASS` only if all checks pass.
- `quality_reason = NULL` when `PASS`.

**Example:** NULL customer_id + invalid customer_id → `INVALID_CUSTOMER_FK,NULL_CUSTOMER_ID`

---

## Quality Metrics (GA-7)

Written to `silver_quality_metrics` after each Silver run.

### Overall row (check_name = `OVERALL`)

- `passed_rows` = count where `quality_status = 'PASS'`
- `failed_rows` = count where `quality_status = 'FAIL'`
- Percentages over `total_rows`

### Per-check rows

For each check code, count rows where that code appears in `quality_reason` (or equivalent check logic).

| table_name | check_name | Purpose |
|------------|------------|---------|
| customers | NULL_EMAIL | Completeness metric |
| customers | DUPLICATE_PK | Uniqueness metric |
| customers | INVALID_SEGMENT | Business metric |
| customers | OVERALL | Entity summary |
| orders | NULL_CUSTOMER_ID | Completeness |
| orders | NULL_PRODUCT_ID | Completeness |
| orders | INVALID_CUSTOMER_FK | RI |
| orders | INVALID_PRODUCT_FK | RI |
| orders | DUPLICATE_PK | Uniqueness |
| orders | INVALID_ORDER_STATUS | Business |
| orders | OVERALL | Entity summary |
| products | DUPLICATE_PK | Uniqueness |
| products | OVERALL | Entity summary |

---

## Gold Inclusion Rules (GA-3)

| Layer | Rule |
|-------|------|
| silver_orders | Include only `quality_status = 'PASS'` AND `order_status = 'Completed'` for revenue aggregations |
| silver_customers | Include only `quality_status = 'PASS'` for dimension joins |
| silver_products | Include only `quality_status = 'PASS'` for dimension joins |

FAIL rows remain in Silver for audit; excluded from Gold joins only.

---

## Validation Approach (GA-1)

**Primary validation target:** 460 explicit source defects (requirements analysis).

| Check | Expected Fail Rows |
|-------|-------------------|
| NULL_EMAIL | 50 |
| DUPLICATE_PK (customers) | 10 |
| NULL_CUSTOMER_ID | 100 |
| NULL_PRODUCT_ID | 200 |
| INVALID_CUSTOMER_FK | 50 |
| INVALID_PRODUCT_FK | 30 |
| DUPLICATE_PK (orders) | 20 |

Note: A single row may fail multiple checks; per-check counts may overlap. Overall FAIL row counts will differ from per-check sums.

The specification's ~700 figure is treated as approximate and non-binding for test assertions.

---

## Failure Case Handling

| Case | Expected Behavior |
|------|-------------------|
| All rows FAIL in entity | Silver completes; metrics show 100% fail; Gold may be empty |
| Invalid enum in source | Row flagged FAIL; pipeline continues |
| Overlapping failures on one row | All codes recorded; single FAIL status |
| Clean products entity | 100% pass expected on OVERALL |

Document any metric variance during Phase 8/9 in `debugging-notes.md`.
