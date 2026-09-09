# Databricks notebook source
"""Silver layer orchestrator: clean, validate, write Silver tables and quality metrics."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from quality_checks import build_metrics
from silver_common import get_spark, read_bronze, write_silver
from silver_pipeline import process_customers, process_orders, process_products

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CUSTOMER_CHECKS = ["NULL_EMAIL", "DUPLICATE_PK", "INVALID_SEGMENT"]
ORDER_CHECKS = [
    "NULL_CUSTOMER_ID",
    "NULL_PRODUCT_ID",
    "INVALID_CUSTOMER_FK",
    "INVALID_PRODUCT_FK",
    "DUPLICATE_PK",
    "INVALID_ORDER_STATUS",
]
PRODUCT_CHECKS = ["DUPLICATE_PK"]


def run_silver_pipeline(spark) -> dict[str, int]:
    run_ts_value = datetime.now(timezone.utc)

    bronze_products = read_bronze(spark, "bronze_products")
    bronze_customers = read_bronze(spark, "bronze_customers")
    bronze_orders = read_bronze(spark, "bronze_orders")

    silver_products = process_products(bronze_products)
    silver_customers = process_customers(bronze_customers)
    silver_orders = process_orders(bronze_orders, bronze_customers, bronze_products)

    results = {
        "silver_products": write_silver(silver_products, "silver_products"),
        "silver_customers": write_silver(silver_customers, "silver_customers"),
        "silver_orders": write_silver(silver_orders, "silver_orders"),
    }

    metrics_dfs = [
        build_metrics(silver_customers, "customers", CUSTOMER_CHECKS, run_ts_value),
        build_metrics(silver_orders, "orders", ORDER_CHECKS, run_ts_value),
        build_metrics(silver_products, "products", PRODUCT_CHECKS, run_ts_value),
    ]

    quality_metrics = metrics_dfs[0]
    for metrics_df in metrics_dfs[1:]:
        quality_metrics = quality_metrics.unionByName(metrics_df)

    results["silver_quality_metrics"] = write_silver(quality_metrics, "silver_quality_metrics")

    logger.info("Silver pipeline complete: %s", results)
    quality_metrics.show(truncate=False)
    return results


if __name__ == "__main__":
    spark = get_spark()
    validation_results = run_silver_pipeline(spark)

    for table_name, row_count in validation_results.items():
        print(f"{table_name}: {row_count} rows written")

    print("Silver pipeline complete.")
