# Debugging Notes

## Phase 8 — Testing & Validation

**Status:** No implementation defects recorded.

Local/static validation passed (`test_source_data.py`, `test_static_validation.py`). Databricks integration validation queries provided in `src/testing/sql/databricks_validation_queries.sql` — execution evidence not yet attached to this document.

If Databricks query results diverge from expected counts in `data-quality-strategy.md`, document variance here with:

- Affected phase (Bronze / Silver / Gold / Dashboard)
- Query or test that failed
- Expected vs actual values
- Whether fix is required in Phase 9

---

## Defect Log

| ID | Phase | Description | Status |
|----|-------|-------------|--------|
| D-1 | Silver (Phase 5) | `silver_orders` row count (100,125) exceeded `bronze_orders` (100,020) by 105 | FIXED |

### D-1 — Silver orders row multiplication

**Symptom:** Databricks validation query showed `bronze_count=100020`, `silver_count=100125` for orders.

**Root cause:** `validate_orders()` in `quality_checks.py` left-joined orders to full `bronze_customers` / `bronze_products` without deduplicating parent PKs. Bronze contains 10 intentional duplicate `customer_id` rows; each order referencing those IDs matched two parent rows, producing duplicate Silver order rows (violates FR-7 / AC-6).

**Affected file:** `src/silver/quality_checks.py`

**Approved requirement:** `data-quality-strategy.md` EC-3 — build valid FK sets from **distinct** Bronze PK values; duplicates remain in the valid set but must not multiply child rows.

**Correction:** Added `.distinct()` to customer and product FK lookup DataFrames before join.

**Re-validation:** Static test `test_validate_orders_uses_distinct_fk_lookups` added. **Databricks re-run required:** re-execute `validate_all.py`, then Bronze=Silver count query — expected `100020` for both.
