# Tool Workflow

Documents how AI-assisted development and Databricks execution were used on this project.

## Development environment

| Tool | Role |
|------|------|
| **Cursor IDE** | Primary editor; AI-assisted implementation per phase |
| **Python 3** | Data generation, local validation tests |
| **Databricks** | PySpark pipeline execution, SQL validation, dashboard |
| **Unity Catalog** | `` `ai-assesment-medillion-structure` `` catalog for Bronze/Silver/Gold tables |

## AI-assisted phase workflow

Each phase followed: **READ → VALIDATE → IMPLEMENT → TEST → DOCUMENT → GATE → STOP**

| Phase | AI prompt history |
|-------|-------------------|
| 0–1 | `ai-prompts/requirements.md` |
| 2 | `ai-prompts/architecture.md` |
| 3 | `ai-prompts/data-generation.md` |
| 4 | `ai-prompts/bronze.md` |
| 5 | `ai-prompts/silver.md` |
| 6 | `ai-prompts/gold.md` |
| 7 | `ai-prompts/dashboard.md` |
| 8 | `ai-prompts/testing.md` |
| 9 | `ai-prompts/debugging.md` |
| 10 | `ai-prompts/documentation.md` |

**Rules applied:** No invented requirements; phase gates enforced; implementation changes only for genuine defects (D-1 in Phase 9).

## Databricks execution workflow

1. Generate or upload CSVs to Volume path (`/Volumes/ai-data_assesment/data-location/raw-data/`)
2. Run Bronze ingestion jobs
3. Run Silver validation (`validate_all.py`) + create trusted views SQL
4. Run Gold mart build
5. Execute validation queries (`src/testing/sql/databricks_validation_queries.sql`)
6. Build dashboard from `src/dashboard/dashboard_queries.sql`

## Local validation workflow

```bash
python3 src/testing/test_source_data.py
python3 src/testing/test_static_validation.py
```

No Java/Spark required for local tests. Full integration validation requires Databricks (documented in `DATABRICKS_VALIDATION_RESULTS.md`).

## Source of truth hierarchy

1. Original project specification
2. Approved phase artifacts (`requirements-analysis.md`, `design-notes.md`, etc.)
3. `PROJECT_STATUS.md` phase approvals
4. Implementation under `src/`
5. Validation evidence under `src/testing/`
