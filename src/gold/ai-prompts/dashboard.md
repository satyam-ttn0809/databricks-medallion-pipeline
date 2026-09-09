# AI Prompt History — Phase 7: Dashboard

### Prompt

START PHASE 7 — DASHBOARD. Verify Phase 6 APPROVED. Create `dashboard_queries.sql`, `DASHBOARD_GUIDE.md`, `ai-prompts/dashboard.md`. Implement Top 10 products, customer revenue distribution, customer segmentation from approved Gold tables only. No assumptions, no Silver/Gold changes, no Phase 8 testing. Stop at Phase 7 gate.

### AI Response Summary

Verified Phase 6 APPROVED. Implemented three dashboard SQL queries in `src/dashboard/dashboard_queries.sql` sourcing exclusively from `gold_sales_by_product`, `gold_revenue_by_customer`, and `gold_customer_segmentation`. Added visualization guidance in `DASHBOARD_GUIDE.md` per design-notes.md (bar chart, bar/histogram, bar/pie). GA-4 revenue buckets (0–500, 501–2000, 2001–5000, 5001+) applied on `gold_revenue_by_customer.total_revenue`.

### Accepted

- design-notes.md Dashboard Design: query sources, GA-4 buckets, visualization types
- data-model.md Dashboard Data Sources and Gold column schemas
- FR-13–FR-16 / DB-1–DB-4: three query areas, ≥3 visualizations
- A-7: dashboard reads Gold-layer outputs only
- Unity Catalog naming: `` `ai-assesment-medillion-structure`.`gold`.`<table>` ``

### Changed

- Added `src/dashboard/dashboard_queries.sql`
- Added `src/dashboard/DASHBOARD_GUIDE.md`
- Added `ai-prompts/dashboard.md`
- Updated `PROJECT_STATUS.md` — Phase 7 READY_FOR_REVIEW

### Rejected

- Reading Silver/Bronze in dashboard SQL — violates layer boundary
- Alternative GA-4 distributions (percentiles, segment-based) — GA-4 resolved in design-notes
- Additional dashboard metrics or visualizations — not in spec
- Claiming Databricks execution success without runtime evidence

### Reason

Approved artifacts fully define dashboard query sources, revenue distribution buckets, and visualization guidance. Gold marts are the trusted consumption layer; dashboard applies presentation-only SQL (Top 10 limit, GA-4 bucketing) with no DQ or business-rule changes.
