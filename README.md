# Databricks Medallion Pipeline

Evaluation-scoped e-commerce analytics pipeline on Databricks using the medallion architecture:

**Source CSVs → Bronze → Silver → Gold → Dashboard**

Unity Catalog: `` `ai-assesment-medillion-structure` ``

## Architecture

```
data/*.csv
    → Bronze (bronze_* Delta tables)
    → Silver (silver_* + silver_quality_metrics + trusted/rejected views)
    → Gold (gold_* marts)
    → Dashboard (SQL queries + Databricks visualizations)
```

| Layer | Responsibility | Key modules |
|-------|----------------|-------------|
| **Source** | Deterministic sample CSVs with intentional DQ defects | `src/data_generation/` |
| **Bronze** | Raw ingestion; explicit schemas; ingestion metadata | `src/bronze/` |
| **Silver** | DQ checking, cleaning (approved rules), validation, trusted data | `src/silver/` |
| **Gold** | Approved business aggregations from trusted Silver | `src/gold/` |
| **Dashboard** | Presentation SQL over Gold marts only | `src/dashboard/` |

## Silver layer (four responsibilities)

Silver is **not** validation-only. Per approved design:

1. **Data-quality checking** — completeness, uniqueness, RI, business/type checks (`quality_checks.py`)
2. **Data cleaning** — approved pass-through preservation + GA-5 duplicate-PK flagging (`silver_cleaning.py`, `SILVER_LAYER_RULES.md`)
3. **Validation** — clean → validate pipeline; `quality_status` / `quality_reason` on every row (`silver_pipeline.py`)
4. **Trusted data** — `silver_*_trusted` (PASS), `silver_*_rejected` (FAIL) views; metrics in `silver_quality_metrics`

Invalid records are **flagged and retained**, not silently deleted (FR-7).

## Repository layout

```
├── requirements-analysis.md    # Phase 1 — FR/NFR/AC
├── design-notes.md             # Phase 2 — architecture decisions
├── data-model.md               # Schemas and lineage
├── data-quality-strategy.md    # DQ checks, metrics, Gold inclusion rules
├── debugging-notes.md          # Phase 9 defect log
├── reflection.md               # Engineering reflection
├── final-ai-usage-summary.md   # AI usage evidence
├── src/
│   ├── data_generation/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── dashboard/
│   └── testing/
└── ai-prompts/                 # Per-phase AI prompt history
```

## Execution (Databricks)

**Prerequisites:** UC schemas `bronze`, `silver`, `gold` in catalog `` `ai-assesment-medillion-structure` ``

| Order | Script | Output |
|-------|--------|--------|
| 1 | `src/data_generation/generate_sample_data.py` | CSVs in Volume or `data/` |
| 2 | `src/bronze/ingest_all.py` | `bronze_*` |
| 3 | `src/silver/validate_all.py` | `silver_*`, `silver_quality_metrics` |
| 4 | `src/silver/sql/silver_trusted_views.sql` | Trusted/rejected views |
| 5 | `src/gold/build_marts.py` | `gold_*` marts |
| 6 | `src/dashboard/dashboard_queries.sql` | Dashboard visualizations |

## Validation evidence

| Evidence | Location |
|----------|----------|
| Local/static tests | `src/testing/test_source_data.py`, `test_static_validation.py` |
| Databricks validation SQL | `src/testing/sql/databricks_validation_queries.sql` |
| Recorded results (user-confirmed) | `src/testing/DATABRICKS_VALIDATION_RESULTS.md` |

## Traceability

```
Specification → requirements-analysis.md
             → design-notes.md / data-model.md / data-quality-strategy.md
             → src/ implementation
             → src/testing/ validation
             → debugging-notes.md (Phase 9)
             → this README + reflection.md + final-ai-usage-summary.md
```

## Phase status

See `PROJECT_STATUS.md` for current phase gate.
