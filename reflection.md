# Reflection

## What was built

A full medallion pipeline: deterministic source data with 460 explicit DQ defects, Bronze raw ingestion, Silver DQ/cleaning/validation/trusted outputs, three Gold marts, and a Databricks SQL dashboard — all traced to approved requirements (FR-1–FR-18, AC-1–AC-15).

## Silver layer — key engineering decisions

### Four responsibilities, not validation-only

Silver was implemented as four explicit concerns:

| Responsibility | Implementation | Evidence |
|----------------|----------------|----------|
| DQ checking | `quality_checks.py` check matrix | `data-quality-strategy.md`, Databricks per-check metrics PASS |
| Cleaning | `silver_cleaning.py` pass-through + GA-5 via validation | `SILVER_LAYER_RULES.md`, Bronze/Silver column compare PASS |
| Validation | `silver_pipeline.py` clean → validate | Static tests, pipeline order |
| Trusted data | `silver_*_trusted` / `_rejected` views + metrics | Databricks view checks PASS |

**Trade-off:** The specification does not define business-value repair rules (NULL imputation, FK correction). Cleaning is therefore **quality enforcement through flagging**, not value correction. This matches FR-7 and avoids inventing rules.

### Invalid record handling

- All Bronze rows written to Silver (AC-6: Bronze = Silver counts after D-1 fix)
- FAIL rows retained with `quality_reason` codes
- Gold excludes FAIL rows per GA-3; Dashboard reads Gold only

### Phase 9 learning (D-1)

RI validation joins must use **distinct** parent PK sets (EC-3) and avoid chained joins referencing the original DataFrame. Row multiplication in Silver violated FR-7 before fix; row-count guard now fails fast.

**Trade-off:** Join-based RI checks are readable but require careful cardinality control. Alternative `isin`/semi-join patterns would also preserve row counts.

## Gold layer

Revenue and order metrics use PASS Silver rows + Completed orders only (GA-3). `lifetime_value_actual` is derived from orders, not source `lifetime_value` (GA-2).

## Testing approach

- Local: source defect counts + static layer-boundary tests
- Databricks: full pipeline validation SQL
- Results: `DATABRICKS_VALIDATION_RESULTS.md` (user-confirmed 2026-09-09)

## What I would not change

- Flag-and-retain DQ strategy (spec-mandated)
- Unity Catalog `saveAsTable` pattern (Databricks deployment constraint discovered in Phases 4–6)
- Minimal Gold/Dashboard scope (no undocumented marts or KPIs)

## AI usage

AI accelerated boilerplate, phase-gated implementation, and documentation drafting. Phase gates, specification traceability, and Databricks execution remained human-validated. See `final-ai-usage-summary.md`.
