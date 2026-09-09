# Testing & Validation Notes — Phase 8

## Phase Gate

- Phases 0–7: APPROVED (`PROJECT_STATUS.md`)
- Phase 8 objective: validate implemented pipeline against approved requirements (AC-1–AC-15)
- **No implementation changes** in this phase unless genuine defect discovered (record in `debugging-notes.md` for Phase 9)

## Validation Scope (per design-notes.md Testing Strategy)

| Level | Artifact | What is validated |
|-------|----------|-------------------|
| Unit | `test_source_data.py` | Source CSV row counts + 460 explicit defects (AC-1, AC-2, GA-1) |
| Unit | `test_static_validation.py` | Layer boundaries, DQ codes, pass-through cleaning, Gold/Dashboard sources |
| Integration | `sql/databricks_validation_queries.sql` | Bronze → Silver → Gold row lineage, DQ metrics, Gold rules |
| SQL | `src/dashboard/dashboard_queries.sql` | Gold-only reads; three query areas (AC-10) |
| Manual | Databricks SQL Dashboard | ≥3 visualizations wired (AC-11) — user confirmed Phase 7 |

## Silver-Layer Responsibility Validation

Per approved Silver design (`SILVER_LAYER_RULES.md`, `data-quality-strategy.md`):

| # | Requirement | How validated |
|---|-------------|---------------|
| 1 | Applies required DQ checks | Static: `quality_checks.py` codes match check matrix; Databricks: `silver_quality_metrics` per-check counts |
| 2 | Cleans per approved rules | Static: `silver_cleaning.py` pass-through (no business correction); Databricks: Bronze/Silver business column compare |
| 3 | Validates cleaned data | Static: `silver_pipeline.py` clean → validate order |
| 4 | Produces trusted datasets | Databricks: `silver_*_trusted` views = PASS rows only |
| 5 | Invalid records per strategy | Databricks: FAIL rows in base tables + `silver_*_rejected` views; no row-count loss Bronze→Silver |
| 6 | No silent record loss | Databricks: Bronze count = Silver count per entity |
| 7 | DQ metrics produced | Databricks: `silver_quality_metrics` overall + per-check rows (GA-7) |

**Approved cleaning rule:** No NULL imputation, FK repair, or enum replacement. Quality enforced via `quality_status` / `quality_reason` flags only.

## Expected DQ Failure Counts (GA-1)

From `data-quality-strategy.md` — per-check `failed_rows` in `silver_quality_metrics`:

| Entity | Check | Expected failures |
|--------|-------|-------------------|
| customers | NULL_EMAIL | 50 |
| customers | DUPLICATE_PK | 10 |
| customers | INVALID_SEGMENT | 0 |
| orders | NULL_CUSTOMER_ID | 100 |
| orders | NULL_PRODUCT_ID | 200 |
| orders | INVALID_CUSTOMER_FK | 50 |
| orders | INVALID_PRODUCT_FK | 30 |
| orders | DUPLICATE_PK | 20 |
| orders | INVALID_ORDER_STATUS | 0 |
| products | DUPLICATE_PK | 0 |

Note: Per-check counts may overlap on multi-failure rows (EC-1). OVERALL FAIL counts will not equal sum of per-check counts.

## Local Test Execution

From repository root:

```bash
python3 src/testing/test_source_data.py
python3 src/testing/test_static_validation.py
```

**Requires:** `data/*.csv` present (Phase 3 output). No Java/Spark required.

## Databricks Test Execution (required for full E2E)

Run in order after pipeline is populated:

1. Bronze: `ingest_all.py` (or per-entity scripts)
2. Silver: `validate_all.py` + `sql/silver_trusted_views.sql`
3. Gold: `build_marts.py`
4. Validation: `src/testing/sql/databricks_validation_queries.sql` (section by section)
5. Dashboard: `src/dashboard/dashboard_queries.sql` (user confirmed visualizations in Phase 7)

**Evidence required for Phase 8 APPROVED:**

- Query output screenshots or copied results for row-count checks (Bronze = Silver)
- `silver_quality_metrics` output matching expected per-check failures
- Gold mart row counts > 0 (unless all rows fail — not expected with sample data)
- Dashboard queries return results (Phase 7 evidence accepted for AC-11 if already confirmed)

## Acceptance Criteria Mapping

| ID | Local static/source | Databricks required |
|----|---------------------|---------------------|
| AC-1 | `test_source_data.py` | Bronze row counts |
| AC-2 | `test_source_data.py` | Silver metrics per-check |
| AC-3 | `test_static_validation.py` | Bronze schema/metadata |
| AC-4 | `test_static_validation.py` | Bronze metadata non-null |
| AC-5 | `test_static_validation.py` | Silver metrics |
| AC-6 | `test_static_validation.py` | Bronze=Silver counts |
| AC-7 | `test_static_validation.py` | quality_status distribution |
| AC-8 | `test_static_validation.py` | silver_quality_metrics |
| AC-9 | `test_static_validation.py` | Gold mart queries |
| AC-10 | `test_static_validation.py` | Dashboard SQL execution |
| AC-11 | — | Dashboard UI (Phase 7 user evidence) |
| AC-12–AC-14 | Code review via static tests | — |
| AC-15 | Phase artifacts present | — |

## Defects

No implementation defects identified during local/static validation. Databricks integration results pending user execution evidence. Record any variances in `debugging-notes.md` (Phase 9).
