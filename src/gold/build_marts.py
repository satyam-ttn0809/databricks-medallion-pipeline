# Databricks notebook source
"""Gold layer: build analytics marts from validated Silver data.

Business rules: see GOLD_BUSINESS_RULES.md
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from gold_common import get_spark, read_silver, write_gold

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def qualifying_orders(orders: DataFrame) -> DataFrame:
    return orders.filter(
        (F.col("quality_status") == "PASS") & (F.col("order_status") == "Completed")
    )


def passed_only(df: DataFrame) -> DataFrame:
    return df.filter(F.col("quality_status") == "PASS")


def build_sales_by_product(orders: DataFrame, products: DataFrame) -> DataFrame:
    joined = qualifying_orders(orders).join(
        passed_only(products),
        on="product_id",
        how="inner",
    )
    return (
        joined.groupBy("product_id", "product_name", "category")
        .agg(
            F.count(F.lit(1)).alias("total_orders"),
            F.sum("total_amount").cast("decimal(18,2)").alias("total_revenue"),
        )
        .withColumn(
            "avg_order_value",
            (F.col("total_revenue") / F.col("total_orders")).cast("decimal(18,2)"),
        )
    )


def build_revenue_by_customer(orders: DataFrame, customers: DataFrame) -> DataFrame:
    joined = qualifying_orders(orders).join(
        passed_only(customers),
        on="customer_id",
        how="inner",
    )
    return (
        joined.groupBy("customer_id", "customer_name", "customer_segment")
        .agg(
            F.count(F.lit(1)).alias("total_orders"),
            F.sum("total_amount").cast("decimal(18,2)").alias("total_revenue"),
        )
        .withColumn(
            "avg_order_value",
            (F.col("total_revenue") / F.col("total_orders")).cast("decimal(18,2)"),
        )
        .withColumn("lifetime_value_actual", F.col("total_revenue"))
    )


def build_customer_segmentation(orders: DataFrame, customers: DataFrame) -> DataFrame:
    customer_revenue = (
        qualifying_orders(orders)
        .join(passed_only(customers), on="customer_id", how="inner")
        .groupBy("customer_id", "customer_segment")
        .agg(F.sum("total_amount").cast("decimal(18,2)").alias("customer_total_revenue"))
    )
    return (
        customer_revenue.groupBy(F.col("customer_segment").alias("segment_type"))
        .agg(
            F.countDistinct("customer_id").alias("customer_count"),
            F.avg("customer_total_revenue").cast("decimal(18,2)").alias("avg_revenue"),
            F.sum("customer_total_revenue").cast("decimal(18,2)").alias("total_revenue"),
        )
    )


def validate_sales_by_product(df: DataFrame) -> None:
    invalid = df.filter(
        (F.col("total_orders") <= 0)
        | F.col("total_revenue").isNull()
        | F.col("avg_order_value").isNull()
        | F.col("product_id").isNull()
    ).count()
    if invalid > 0:
        raise ValueError(f"gold_sales_by_product validation failed: {invalid} invalid rows")


def validate_revenue_by_customer(df: DataFrame) -> None:
    mismatch = df.filter(F.col("lifetime_value_actual") != F.col("total_revenue")).count()
    invalid = df.filter(
        (F.col("total_orders") <= 0)
        | F.col("total_revenue").isNull()
        | F.col("lifetime_value_actual").isNull()
        | F.col("customer_id").isNull()
    ).count()
    if mismatch > 0 or invalid > 0:
        raise ValueError(
            f"gold_revenue_by_customer validation failed: "
            f"{mismatch} lifetime mismatches, {invalid} invalid rows"
        )


def validate_customer_segmentation(df: DataFrame) -> None:
    invalid = df.filter(
        F.col("segment_type").isNull()
        | (F.col("customer_count") <= 0)
        | F.col("total_revenue").isNull()
        | F.col("avg_revenue").isNull()
    ).count()
    if invalid > 0:
        raise ValueError(f"gold_customer_segmentation validation failed: {invalid} invalid rows")


def run_gold_build(spark) -> dict[str, int]:
    silver_orders = read_silver(spark, "silver_orders")
    silver_customers = read_silver(spark, "silver_customers")
    silver_products = read_silver(spark, "silver_products")

    sales_by_product = build_sales_by_product(silver_orders, silver_products)
    revenue_by_customer = build_revenue_by_customer(silver_orders, silver_customers)
    customer_segmentation = build_customer_segmentation(silver_orders, silver_customers)

    validate_sales_by_product(sales_by_product)
    validate_revenue_by_customer(revenue_by_customer)
    validate_customer_segmentation(customer_segmentation)

    logger.info("Gold mart validations passed")

    return {
        "gold_sales_by_product": write_gold(sales_by_product, "gold_sales_by_product"),
        "gold_revenue_by_customer": write_gold(revenue_by_customer, "gold_revenue_by_customer"),
        "gold_customer_segmentation": write_gold(
            customer_segmentation, "gold_customer_segmentation"
        ),
    }


spark = get_spark()
results = run_gold_build(spark)

for table_name, row_count in results.items():
    print(f"{table_name}: {row_count} rows written")

print("Gold layer build complete.")
