# Silver Layer Rules

## Cleaning vs Validation (per approved artifacts)

| Concept | Approved behaviour |
|---------|-------------------|
| **Validation** | Detect issues; set `quality_status` / `quality_reason` |
| **Cleaning** | No business-value correction rules are defined in spec |
| **Trusted data** | Rows with `quality_status = 'PASS'` (Gold uses PASS only per GA-3) |
| **Rejected data** | Rows with `quality_status = 'FAIL'` (retained in Silver for audit) |

## Cleaning implemented

| Rule | Source | Action |
|------|--------|--------|
| Preserve Bronze business values | design-notes BR-2 / SV input | Pass-through in `silver_cleaning.py` |
| Duplicate PK resolution | GA-5 | Flag `row_number > 1` as `DUPLICATE_PK`; first row eligible for PASS |
| NULL / invalid FK / invalid enum | data-quality-strategy | **Detect and flag only** — no imputation or repair defined |

## Not implemented (no spec rule)

- NULL email imputation
- NULL FK replacement
- Invalid FK correction
- Enum value standardization/replacement
- Silent row deletion

## Bad record handling

- All Bronze rows written to Silver entity tables
- FAIL rows are **not** deleted (FR-7, NFR-11)
- Trusted views: `silver_*_trusted` (PASS only)
- Rejected views: `silver_*_rejected` (FAIL only)

## Intentional Phase 3 defects — expected detection

| Check | Expected failures |
|-------|-------------------|
| NULL_EMAIL | 50 |
| DUPLICATE_PK (customers) | 10 |
| NULL_CUSTOMER_ID | 100 |
| NULL_PRODUCT_ID | 200 |
| INVALID_CUSTOMER_FK | 50 |
| INVALID_PRODUCT_FK | 30 |
| DUPLICATE_PK (orders) | 20 |

## Unity Catalog targets

- Bronze read: `` `ai-assesment-medillion-structure`.`bronze`.`bronze_*` ``
- Silver write: `` `ai-assesment-medillion-structure`.`silver`.`silver_*` ``
- Metrics: `` `ai-assesment-medillion-structure`.`silver`.`silver_quality_metrics` ``
