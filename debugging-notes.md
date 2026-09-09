# Debugging Notes

## Phase 9 — Summary

One defect (D-1) identified in Phase 8 Databricks validation, corrected in Silver, re-validated successfully. All pipeline validation queries pass.

---

## Defect Log

| ID | Phase | Description | Status |
|----|-------|-------------|--------|
| D-1 | Silver (Phase 5) | `silver_orders` row count exceeded `bronze_orders` by 105 | **FIXED & VERIFIED** |

### D-1 — Silver orders row multiplication

**Symptom:** Databricks validation showed `bronze_count=100020`, `silver_count=100125` for orders.

**Root cause:** `validate_orders()` in `quality_checks.py` left-joined orders to non-distinct `bronze_customers` / `bronze_products`. Ten intentional duplicate `customer_id` rows in Bronze caused 105 order rows (referencing those IDs) to multiply.

**Affected file:** `src/silver/quality_checks.py`

**Approved requirement:** `data-quality-strategy.md` EC-3 — FK sets from **distinct** Bronze PK values; no row loss or gain (FR-7, AC-6).

**Correction:**

1. `.distinct()` on customer and product FK lookup DataFrames
2. Two-step join using `enriched.product_id` (not chained `df.product_id`)
3. Runtime row-count guard — raises if input/output counts differ

**Re-validation (2026-09-09, user-confirmed Databricks):**

| check | result |
|-------|--------|
| Bronze = Silver orders (100,020) | PASS |
| Bronze = Silver customers (10,010) | PASS |
| Bronze = Silver products (500) | PASS |
| silver_customers FAIL=60, PASS=9,950 | PASS |
| silver_quality_metrics per-check counts | PASS |
| Gold marts | PASS |
| Dashboard queries | PASS |

Full evidence: `src/testing/DATABRICKS_VALIDATION_RESULTS.md`
