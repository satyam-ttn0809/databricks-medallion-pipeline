# AI Prompt History — Phase 3: Data Generation

### Prompt

START PHASE 3 — DATA GENERATION SCRIPT.

Verify PHASE 2 = APPROVED. Use approved requirements-analysis.md, design-notes.md, data-model.md, data-quality-strategy.md, and original specification.

Create data-generation script only. User executes manually in Databricks. Do NOT generate data, execute script, or claim validation passed.

Create: generate_sample_data.py, DATA_GENERATION_NOTES.md, ai-prompts/data-generation.md.

### AI Response Summary

Verified Phase 2 APPROVED. Created deterministic Python generator with seed=42, defect injection matching spec counts (460 explicit defects), built-in validation functions, and Databricks execution documentation. Did not execute script or create CSV files.

### Accepted

- Approved data model row counts, schemas, and defect counts
- Empty-string NULL representation for CSV fields
- Duplicate rows as verbatim copies of existing PK rows
- Invalid FK values outside valid ID ranges (customer_id > 10000, product_id > 500)
- Output path via `DATA_DIR` env var or `--output-dir` per design A-3
- Phase 3 scope limited to script and documentation only

### Changed

- Default output uses `DATA_DIR` environment variable instead of hardcoded repo path (Databricks execution)
- Phase status set to READY_FOR_REVIEW pending user execution

### Rejected

- Adding products intentional defects — not specified
- Executing script or generating CSV files in repository — user responsibility
- Claiming validation passed — execution not performed
- Bronze/Silver/Gold/Dashboard code — out of scope

### Reason

Phase 3 boundary: LLM delivers script and docs; user runs in Databricks and provides execution results before Phase 4.
