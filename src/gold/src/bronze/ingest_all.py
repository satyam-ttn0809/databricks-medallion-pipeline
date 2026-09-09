# Databricks notebook source
"""Bronze ingestion orchestrator: ingest all source CSVs to Bronze Delta tables."""

from __future__ import annotations

import logging

from bronze_common import get_spark, ingest_customers, ingest_orders, ingest_products

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

spark = get_spark()

results = {
    "bronze_customers": ingest_customers(spark),
    "bronze_orders": ingest_orders(spark),
    "bronze_products": ingest_products(spark),
}

for table_name, row_count in results.items():
    print(f"{table_name}: {row_count} rows ingested")

print("Bronze ingestion complete for all entities.")
