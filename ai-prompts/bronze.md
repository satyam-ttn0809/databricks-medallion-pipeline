# AI Prompt History — Phase 4: Bronze Layer

### Prompt

START PHASE 4 — BRONZE LAYER.

Verify PHASE 3 = APPROVED. Implement only Bronze ingestion.

Create:
- src/bronze/01_ingest_customers.py
- src/bronze/02_ingest_orders.py
- src/bronze/03_ingest_products.py
- src/bronze/ingest_all.py

Source path: `/Volumes/ai-data_assesment/data-location/raw-data/`

Requirements: CSV ingestion, explicit schemas, raw preservation, Bronze Delta tables, ingestion metadata, row-count logging, error handling.

Do not implement Silver, Gold, or Dashboard.

### AI Response Summary

Verified Phase 3 APPROVED. Implemented Bronze ingestion with shared `bronze_common.py` module containing explicit schemas, ingest logic, metadata columns (`_ingestion_timestamp`, `_source_file`), Delta overwrite writes, row-count logging, and FileNotFoundError on missing source. Four entry-point scripts created per prompt. Script-level validation performed; runtime execution deferred to user on Databricks.

### Accepted

- User-specified raw data volume path
- Approved Bronze design: explicit schemas, no business transforms, Delta overwrite, per-row metadata
- Table names: bronze_customers, bronze_orders, bronze_products
- Separate ingest scripts per entity plus orchestrator

### Changed

- Bronze output path: `/Volumes/ai-data_assesment/data-location/bronze/` (parallel to raw-data volume; not explicitly specified by user)
- Added `bronze_common.py` for shared schemas and ingest logic to avoid duplication across four entry scripts

### Rejected

- Silver/Gold/Dashboard code — out of scope
- Business transformations or DQ in Bronze — violates BR-2
- Append-only Bronze writes — rejected per approved design (overwrite mode)

### Reason

Bronze must preserve raw CSV data with explicit schemas and ingestion metadata only. Shared module keeps entry scripts minimal while meeting all Bronze requirements.
