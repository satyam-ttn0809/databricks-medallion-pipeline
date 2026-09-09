# Databricks notebook source
"""Silver: clean and validate orders."""

from __future__ import annotations

import logging

from silver_common import get_spark, read_bronze, write_silver
from silver_pipeline import process_orders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
silver_orders = process_orders(
    read_bronze(spark, "bronze_orders"),
    read_bronze(spark, "bronze_customers"),
    read_bronze(spark, "bronze_products"),
)
row_count = write_silver(silver_orders, "silver_orders")
print(f"silver_orders: {row_count} rows written")
