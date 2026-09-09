# Final AI Usage Summary

## Overview

This project used **Cursor IDE** AI assistance across Phases 0–10. Prompt history is preserved per phase in `ai-prompts/`. AI was used for requirement analysis support, architecture documentation, code generation, test scaffolding, debugging analysis, and final documentation — **not** for fabricating validation results.

## Phase-by-phase AI contribution

| Phase | AI role | Human validation |
|-------|---------|------------------|
| 0–1 | Requirements structuring | Phase 1 APPROVED |
| 2 | Architecture artifacts (assumptions GA-1–GA-8 resolved) | Phase 2 APPROVED |
| 3 | Data generation script | User executes in Databricks |
| 4 | Bronze ingestion modules | Databricks execution |
| 5 | Silver DQ/cleaning/validation pipeline | Databricks execution |
| 6 | Gold marts | Databricks execution |
| 7 | Dashboard SQL + guide | User created dashboard in Databricks |
| 8 | Test scripts + validation SQL | Local tests + user Databricks runs |
| 9 | D-1 root-cause analysis and Silver fix | User re-validated all queries PASS |
| 10 | Final documentation synthesis | This document |

## Prompt history files

- `ai-prompts/requirements.md`
- `ai-prompts/architecture.md`
- `ai-prompts/data-generation.md`
- `ai-prompts/bronze.md`
- `ai-prompts/silver.md`
- `ai-prompts/gold.md`
- `ai-prompts/dashboard.md`
- `ai-prompts/testing.md`
- `ai-prompts/debugging.md`
- `ai-prompts/documentation.md`

## AI decisions accepted (traceable to spec)

- Silver cleaning as pass-through + flagging (no invented repair rules)
- GA-3 Gold inclusion: PASS + Completed orders
- GA-4 dashboard buckets: 0–500, 501–2000, 2001–5000, 5001+
- GA-5 duplicate PK: flag `row_number > 1` only
- Unity Catalog table writes with backtick-quoted catalog name

## AI decisions rejected (per spec or gates)

- Silent deletion of FAIL rows
- Silver business-value correction without spec rule
- Gold/Dashboard workarounds for Silver D-1 defect
- Additional marts, KPIs, or dashboard queries not in FR-13–FR-16
- Claiming Databricks PASS without user execution evidence

## Responsible usage practices followed

1. Phase gates enforced (`PROJECT_STATUS.md`)
2. `BLOCKING_INFORMATION_REQUIRED` used when phases blocked (e.g., Phase 7 before Phase 6 approval)
3. Validation evidence documented separately (`DATABRICKS_VALIDATION_RESULTS.md`)
4. Defects recorded in `debugging-notes.md` before fix
5. No hardcoded secrets introduced

## Candidate accountability

The candidate reviewed AI-generated code and documentation, executed pipeline jobs in Databricks, confirmed validation results, and approved phase gates. Personal details: see `candidate-info.md`.
