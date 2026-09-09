"""Static validation of layer boundaries, schemas, and approved artifacts.

No Spark required. Confirms implementation aligns with approved requirements
without modifying Bronze/Silver/Gold/Dashboard code.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BRONZE_BUSINESS_COLUMNS = {
    "customers": {
        "customer_id",
        "customer_name",
        "email",
        "country",
        "signup_date",
        "customer_segment",
        "lifetime_value",
    },
    "orders": {
        "order_id",
        "customer_id",
        "order_date",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "order_status",
        "payment_date",
    },
    "products": {
        "product_id",
        "product_name",
        "category",
        "price",
        "cost",
        "stock_quantity",
        "reorder_level",
    },
}

SILVER_QUALITY_COLUMNS = {"quality_status", "quality_reason"}
BRONZE_METADATA_COLUMNS = {"_ingestion_timestamp", "_source_file"}

GOLD_MART_COLUMNS = {
    "gold_sales_by_product": {
        "product_id",
        "product_name",
        "category",
        "total_orders",
        "total_revenue",
        "avg_order_value",
    },
    "gold_revenue_by_customer": {
        "customer_id",
        "customer_name",
        "customer_segment",
        "total_orders",
        "total_revenue",
        "avg_order_value",
        "lifetime_value_actual",
    },
    "gold_customer_segmentation": {
        "segment_type",
        "customer_count",
        "avg_revenue",
        "total_revenue",
    },
}

EXPECTED_DQ_CODES = {
    "customers": ["NULL_EMAIL", "DUPLICATE_PK", "INVALID_SEGMENT"],
    "orders": [
        "NULL_CUSTOMER_ID",
        "NULL_PRODUCT_ID",
        "INVALID_CUSTOMER_FK",
        "INVALID_PRODUCT_FK",
        "DUPLICATE_PK",
        "INVALID_ORDER_STATUS",
    ],
    "products": ["DUPLICATE_PK"],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_bronze_schema_preserves_source_columns() -> None:
    bronze = _read(REPO_ROOT / "src/bronze/bronze_common.py")
    for entity, cols in BRONZE_BUSINESS_COLUMNS.items():
        for col in cols:
            assert f'"{col}"' in bronze, f"Bronze missing column {col} for {entity}"
    for meta in BRONZE_METADATA_COLUMNS:
        assert meta in bronze, f"Bronze missing metadata column {meta}"


def test_bronze_does_not_apply_business_transforms() -> None:
    bronze = _read(REPO_ROOT / "src/bronze/bronze_common.py")
    ingest_section = bronze.split("def ingest_csv_to_bronze")[1].split("def ingest_customers")[0]
    assert "quality_status" not in ingest_section
    assert "quality_reason" not in ingest_section
    assert "drop(" not in ingest_section
    assert "filter(" not in ingest_section
    # Approved metadata only (GA-6): _ingestion_timestamp, _source_file
    assert "_ingestion_timestamp" in ingest_section
    assert "_source_file" in ingest_section
    assert ingest_section.count("withColumn(") == 2


def test_silver_cleaning_is_pass_through() -> None:
    cleaning = _read(REPO_ROOT / "src/silver/silver_cleaning.py")
    for fn in ("clean_customers", "clean_orders", "clean_products"):
        assert f"def {fn}" in cleaning
        body = cleaning.split(f"def {fn}")[1].split("\n\n")[0]
        assert "return df" in body
        assert "drop(" not in body
        assert "filter(" not in body


def test_silver_pipeline_order_clean_then_validate() -> None:
    pipeline = _read(REPO_ROOT / "src/silver/silver_pipeline.py")
    assert "validate_customers(clean_customers" in pipeline
    assert "validate_orders" in pipeline and "clean_orders" in pipeline
    assert "validate_products(clean_products" in pipeline


def test_silver_quality_checks_cover_approved_codes() -> None:
    checks = _read(REPO_ROOT / "src/silver/quality_checks.py")
    for entity, codes in EXPECTED_DQ_CODES.items():
        for code in codes:
            assert f'"{code}"' in checks, f"Missing DQ code {code} for {entity}"
    assert "quality_status" in checks and "quality_reason" in checks
    assert "row_number" in checks  # GA-5 duplicate handling


def test_validate_orders_uses_distinct_fk_lookups() -> None:
    """RI joins must not multiply rows when Bronze parents have duplicate PKs (EC-3)."""
    checks = _read(REPO_ROOT / "src/silver/quality_checks.py")
    orders_fn = checks.split("def validate_orders")[1].split("def build_metrics")[0]
    assert orders_fn.count(".distinct()") >= 2
    assert "enriched.product_id" in orders_fn
    assert "validate_orders changed row count" in orders_fn


def test_silver_metrics_builder_exists() -> None:
    checks = _read(REPO_ROOT / "src/silver/quality_checks.py")
    assert "def build_metrics" in checks
    assert "OVERALL" in checks
    assert "pass_pct" in checks and "fail_pct" in checks


def test_gold_reads_silver_only() -> None:
    gold_common = _read(REPO_ROOT / "src/gold/gold_common.py")
    build_marts = _read(REPO_ROOT / "src/gold/build_marts.py")
    assert "read_silver" in gold_common
    assert "read_bronze" not in build_marts
    assert ".bronze." not in build_marts.lower()
    assert "quality_status" in build_marts
    assert "Completed" in build_marts


def test_gold_mart_builders_present() -> None:
    build_marts = _read(REPO_ROOT / "src/gold/build_marts.py")
    for fn in (
        "build_sales_by_product",
        "build_revenue_by_customer",
        "build_customer_segmentation",
    ):
        assert f"def {fn}" in build_marts


def test_dashboard_reads_gold_only() -> None:
    sql = _read(REPO_ROOT / "src/dashboard/dashboard_queries.sql").lower()
    assert "gold.gold_sales_by_product" in sql
    assert "gold.gold_revenue_by_customer" in sql
    assert "gold.gold_customer_segmentation" in sql
    assert "silver." not in sql
    assert "bronze." not in sql
    assert "quality_status" not in sql


def test_trusted_views_filter_pass_only() -> None:
    views = _read(REPO_ROOT / "src/silver/sql/silver_trusted_views.sql")
    assert "quality_status = 'PASS'" in views
    assert "quality_status = 'FAIL'" in views


def test_dashboard_query_file_has_three_sections() -> None:
    sql = _read(REPO_ROOT / "src/dashboard/dashboard_queries.sql")
    assert "Top 10 products" in sql
    assert "Customer revenue distribution" in sql
    assert "Customer segmentation" in sql
    assert sql.count("LIMIT 10") >= 1


def test_gold_sql_files_no_bronze_reads() -> None:
    for path in (REPO_ROOT / "src/gold/sql").glob("*.sql"):
        content = path.read_text(encoding="utf-8").lower()
        assert "bronze." not in content, f"{path.name} reads Bronze"


def run_all() -> None:
    tests = [
        v
        for k, v in globals().items()
        if k.startswith("test_") and callable(v)
    ]
    for test_fn in tests:
        test_fn()
        print(f"{test_fn.__name__}: PASSED")


if __name__ == "__main__":
    run_all()
