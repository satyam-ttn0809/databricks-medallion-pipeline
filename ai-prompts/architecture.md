# AI Prompt History — Phase 2: Architecture & Data Model

### Prompt

START PHASE 2 — ARCHITECTURE & DATA MODEL.

Verify PHASE 1 = APPROVED. Use requirements-analysis.md as functional source of truth.

Create/update: design-notes.md, data-model.md, data-quality-strategy.md, ai-prompts/architecture.md.

Define architecture, layer responsibilities, schemas, relationships, Bronze/Silver/Gold/DQ design, error-handling, testing strategy, assumptions.

Do NOT implement pipeline code. Do NOT generate sample data. Do NOT start Phase 3.

Validate against requirements-analysis.md. Stop at Phase 2 gate.

### AI Response Summary

Verified Phase 1 APPROVED. Created four architecture artifacts resolving Phase 1 assumptions (A-1–A-7) and ambiguities (GA-1–GA-8) with documented design decisions. Defined simple medallion flow, explicit schemas, DQ flagging strategy, Gold inclusion rules, dashboard SQL sources, error handling, and testing approach. No code or sample data generated.

### Accepted

- requirements-analysis.md as sole functional input
- Simple architecture within specification bounds
- Resolve ambiguities in design docs rather than deferring to implementation
- Flag-not-delete Silver pattern
- Config-driven paths for local and Databricks

### Changed

- GA-1: Use 460 explicit defects for validation; ~700 treated as approximate
- GA-2: `lifetime_value_actual` = sum of Completed PASS order revenue
- GA-3: Gold uses PASS Silver rows + Completed orders for revenue
- GA-4: Revenue distribution = histogram buckets on customer total revenue
- GA-5: Duplicate PK failures on row_number > 1 only
- GA-6: Per-row `_ingestion_timestamp`, `_source_file`; row count logged
- GA-7: Overall + per-check metrics table
- GA-8: Products clean; PK uniqueness only

### Rejected

- Including non-Completed orders in revenue — not specified; would invent business rule without conservative basis
- Using source `lifetime_value` as `lifetime_value_actual` — contradicts "actual" derived semantics
- Silent row deletion in Silver — violates FR-7
- Additional DQ rules (total_amount consistency, payment_date) — not in specification

### Reason

Design must close Phase 1 open items with traceable decisions while staying within spec. Conservative revenue rules (Completed + PASS) produce defensible analytics without inventing unsupported business logic.
