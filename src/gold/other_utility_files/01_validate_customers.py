# Databricks notebook source
"""Silver: clean and validate customers."""

from __future__ import annotations

import logging

from silver_common import get_spark, read_bronze, write_silver
from silver_pipeline import process_customers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
silver_customers = process_customers(read_bronze(spark, "bronze_customers"))
row_count = write_silver(silver_customers, "silver_customers")
print(f"silver_customers: {row_count} rows written")
