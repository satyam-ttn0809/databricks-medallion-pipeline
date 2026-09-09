# Databricks notebook source
"""Bronze ingestion: products.csv -> bronze_products Delta table."""

from __future__ import annotations

import logging

from bronze_common import get_spark, ingest_products

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
row_count = ingest_products(spark)
print(f"bronze_products ingestion complete: {row_count} rows")
