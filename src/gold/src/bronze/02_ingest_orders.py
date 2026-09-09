# Databricks notebook source
"""Bronze ingestion: orders.csv -> bronze_orders Delta table."""

from __future__ import annotations

import logging

from bronze_common import get_spark, ingest_orders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
row_count = ingest_orders(spark)
print(f"bronze_orders ingestion complete: {row_count} rows")
