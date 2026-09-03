"""Silver data-quality check functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from pyspark.sql import functions as F
from pyspark.sql.window import Window

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame

CUSTOMER_SEGMENTS = ("Premium", "Standard", "Basic")
ORDER_STATUSES = ("Pending", "Completed", "Cancelled")


def _failure_array(*conditions: tuple[str, Column]) -> Column:
    """Build a sorted array of failure codes for rows that fail each condition."""
    flags = [
        F.when(condition, F.lit(code)) for code, condition in conditions if condition is not None
    ]
    return F.array_sort(F.array_compact(F.array(*flags)))


def _apply_quality_columns(df: DataFrame, failure_conditions: Iterable[tuple[str, Column]]) -> DataFrame:
    reasons = _failure_array(*failure_conditions)
    return (
        df.withColumn("_failure_codes", reasons)
        .withColumn(
            "quality_reason",
            F.when(F.size(F.col("_failure_codes")) > 0, F.array_join(F.col("_failure_codes"), ",")),
        )
        .withColumn(
            "quality_status",
            F.when(F.size(F.col("_failure_codes")) > 0, F.lit("FAIL")).otherwise(F.lit("PASS")),
        )
        .drop("_failure_codes")
    )


def _duplicate_pk_condition(pk_column: str) -> Column:
    window = Window.partitionBy(pk_column).orderBy(F.col("_ingestion_timestamp"))
    return F.row_number().over(window) > 1


def validate_customers(df: DataFrame) -> DataFrame:
    """Apply completeness, uniqueness, and business validation to customers."""
    null_email = F.col("email").isNull() | (F.trim(F.col("email")) == "")
    duplicate_pk = _duplicate_pk_condition("customer_id")
    invalid_segment = ~F.col("customer_segment").isin(*CUSTOMER_SEGMENTS)

    return _apply_quality_columns(
        df,
        [
            ("NULL_EMAIL", null_email),
            ("DUPLICATE_PK", duplicate_pk),
            ("INVALID_SEGMENT", invalid_segment),
        ],
    )


def validate_products(df: DataFrame) -> DataFrame:
    """Apply uniqueness validation to products."""
    duplicate_pk = _duplicate_pk_condition("product_id")
    return _apply_quality_columns(df, [("DUPLICATE_PK", duplicate_pk)])


def validate_orders(
    df: DataFrame,
    valid_customer_ids: DataFrame,
    valid_product_ids: DataFrame,
) -> DataFrame:
    """Apply completeness, referential integrity, uniqueness, and business validation to orders."""
    customers = valid_customer_ids.select(F.col("customer_id").alias("_valid_customer_id"))
    products = valid_product_ids.select(F.col("product_id").alias("_valid_product_id"))

    enriched = (
        df.join(customers, df.customer_id == customers._valid_customer_id, "left")
        .join(products, df.product_id == products._valid_product_id, "left")
    )

    null_customer_id = F.col("customer_id").isNull()
    null_product_id = F.col("product_id").isNull()
    invalid_customer_fk = F.col("customer_id").isNotNull() & F.col("_valid_customer_id").isNull()
    invalid_product_fk = F.col("product_id").isNotNull() & F.col("_valid_product_id").isNull()
    duplicate_pk = _duplicate_pk_condition("order_id")
    invalid_order_status = ~F.col("order_status").isin(*ORDER_STATUSES)

    result = _apply_quality_columns(
        enriched,
        [
            ("NULL_CUSTOMER_ID", null_customer_id),
            ("NULL_PRODUCT_ID", null_product_id),
            ("INVALID_CUSTOMER_FK", invalid_customer_fk),
            ("INVALID_PRODUCT_FK", invalid_product_fk),
            ("DUPLICATE_PK", duplicate_pk),
            ("INVALID_ORDER_STATUS", invalid_order_status),
        ],
    )
    return result.drop("_valid_customer_id", "_valid_product_id")


def build_metrics(
    df: DataFrame,
    table_name: str,
    check_codes: list[str],
    run_timestamp,
) -> DataFrame:
    """Build overall and per-check quality metrics with pass/fail percentages."""
    total_rows = df.count()
    failed_rows = df.filter(F.col("quality_status") == "FAIL").count()

    def _metric_row(check_name: str, failed_count: int):
        passed_count = total_rows - failed_count
        return (
            table_name,
            check_name,
            total_rows,
            passed_count,
            failed_count,
            round((passed_count / total_rows) * 100, 2) if total_rows else 0.0,
            round((failed_count / total_rows) * 100, 2) if total_rows else 0.0,
            run_timestamp,
        )

    rows = [_metric_row("OVERALL", failed_rows)]

    for code in check_codes:
        failed_count = df.filter(
            F.array_contains(F.split(F.coalesce(F.col("quality_reason"), F.lit("")), ","), code)
        ).count()
        rows.append(_metric_row(code, failed_count))

    schema = (
        "table_name string, check_name string, total_rows long, passed_rows long, "
        "failed_rows long, pass_pct double, fail_pct double, run_timestamp timestamp"
    )
    return df.sparkSession.createDataFrame(rows, schema=schema)
