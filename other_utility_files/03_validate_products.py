# Databricks notebook source
"""Silver: clean and validate products."""

from __future__ import annotations

import logging

from silver_common import get_spark, read_bronze, write_silver
from silver_pipeline import process_products

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
silver_products = process_products(read_bronze(spark, "bronze_products"))
row_count = write_silver(silver_products, "silver_products")
print(f"silver_products: {row_count} rows written")
