# Databricks notebook source
"""Bronze ingestion: customers.csv -> bronze_customers Delta table."""

from __future__ import annotations

import logging

from bronze_common import get_spark, ingest_customers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()
row_count = ingest_customers(spark)
print(f"bronze_customers ingestion complete: {row_count} rows")
