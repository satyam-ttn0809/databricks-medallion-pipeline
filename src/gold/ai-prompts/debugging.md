# AI Prompt History — Phase 9: Debugging & Refinement

### Prompt

User reported Databricks Phase 8 validation failure: `bronze_orders` count 100,020 vs `silver_orders` count 100,125 (105 extra rows). Investigate and fix per approved specification.

### AI Response Summary

Identified root cause in `validate_orders()` RI join: non-distinct Bronze parent PKs caused row multiplication when orders referenced duplicated `customer_id` values (10 intentional Bronze duplicates). Fixed by adding `.distinct()` to FK lookup DataFrames per `data-quality-strategy.md` EC-3. Added static regression test. Databricks re-validation pending user re-run of Silver pipeline.

### Defect D-1

| Field | Detail |
|-------|--------|
| Defect | Silver orders gained 105 rows vs Bronze |
| Root cause | Left join to non-distinct `bronze_customers.customer_id` multiplied rows for duplicate PKs |
| Phase/file | Phase 5 Silver — `src/silver/quality_checks.py` |
| Approved rule | EC-3: distinct PK values for FK validation set; no silent row loss or gain |
| Correction | `.distinct()` on customer and product FK lookup before join |
| Validation | `test_static_validation.py` — `test_validate_orders_uses_distinct_fk_lookups` PASSED locally; Databricks Bronze=Silver count query NOT re-run by agent |

### Rejected

- Fixing in Gold/Dashboard — upstream Silver RI join defect
- Dropping duplicate customer rows in Silver cleaning — not approved; flag-only strategy
- Fabricating Databricks re-validation results
