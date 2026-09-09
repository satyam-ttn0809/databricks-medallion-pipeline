# Databricks Validation Results — Phase 8 / Phase 9 Re-validation

**Execution environment:** Databricks SQL / pipeline jobs  
**Validation date:** 2026-09-09  
**Evidence source:** User-confirmed execution of `src/testing/sql/databricks_validation_queries.sql` and Silver/Gold pipeline re-run after D-1 fix  
**Result:** **ALL CHECKS PASSED**

---

## Pipeline Re-run (after D-1 fix)

| Step | Script | Result |
|------|--------|--------|
| Silver | `validate_all.py` | PASSED — `silver_orders` row-count guard did not fire |
| Gold | `build_marts.py` | PASSED (re-run after Silver fix) |
| Dashboard | `dashboard_queries.sql` | PASSED (Phase 7; re-confirmed) |

---

## AC-1 / AC-2 — Source / Bronze row counts

| table_name | row_count | Expected | Status |
|------------|-----------|----------|--------|
| bronze_customers | 10,010 | 10,010 | PASS |
| bronze_orders | 100,020 | 100,020 | PASS |
| bronze_products | 500 | 500 | PASS |

---

## AC-3 / AC-4 — Bronze metadata

| check | Result |
|-------|--------|
| `_ingestion_timestamp` populated on all rows | PASS |
| `_source_file` populated on all rows | PASS |

---

## AC-6 — Bronze = Silver row counts (no silent loss or gain)

| entity | bronze_count | silver_count | Status |
|--------|--------------|--------------|--------|
| customers | 10,010 | 10,010 | PASS |
| orders | 100,020 | 100,020 | PASS |
| products | 500 | 500 | PASS |

---

## AC-7 — Silver `quality_status` distribution

### silver_customers

| quality_status | row_count | Notes |
|----------------|-----------|-------|
| FAIL | 60 | 50 NULL_EMAIL + 10 DUPLICATE_PK (GA-5) |
| PASS | 9,950 | |
| **Total** | **10,010** | Matches Bronze |

### silver_orders / silver_products

Per-check metrics and OVERALL distribution validated — all match `data-quality-strategy.md` expected counts.

---

## AC-8 — `silver_quality_metrics` per-check failures

| table_name | check_name | expected failed_rows | Status |
|------------|------------|----------------------|--------|
| customers | NULL_EMAIL | 50 | PASS |
| customers | DUPLICATE_PK | 10 | PASS |
| customers | INVALID_SEGMENT | 0 | PASS |
| orders | NULL_CUSTOMER_ID | 100 | PASS |
| orders | NULL_PRODUCT_ID | 200 | PASS |
| orders | INVALID_CUSTOMER_FK | 50 | PASS |
| orders | INVALID_PRODUCT_FK | 30 | PASS |
| orders | DUPLICATE_PK | 20 | PASS |
| orders | INVALID_ORDER_STATUS | 0 | PASS |
| products | DUPLICATE_PK | 0 | PASS |

---

## Silver cleaning / trusted views

| check | Result |
|-------|--------|
| Bronze business columns preserved (pass-through cleaning) | PASS |
| `silver_*_trusted` = PASS rows only | PASS |
| `silver_*_rejected` = FAIL rows only | PASS |

---

## AC-9 — Gold marts

| mart | Result |
|------|--------|
| `gold_sales_by_product` | PASS — populated, valid schema |
| `gold_revenue_by_customer` | PASS — `lifetime_value_actual = total_revenue` |
| `gold_customer_segmentation` | PASS — `segment_type` populated |

---

## AC-10 / AC-11 — Dashboard

| check | Result |
|-------|--------|
| Top 10 products query | PASS |
| Customer revenue distribution (GA-4 buckets) | PASS |
| Customer segmentation query | PASS |
| ≥3 visualizations (Phase 7) | PASS |

---

## Phase 9 defect resolution

| ID | Fix | Re-validation |
|----|-----|---------------|
| D-1 | `quality_checks.py` — distinct FK lookups + two-step join + row-count guard | PASSED — orders Bronze=Silver 100,020 |

---

## Summary

All approved acceptance criteria (AC-1–AC-11) validated in Databricks after Silver D-1 correction. No remaining open defects.
