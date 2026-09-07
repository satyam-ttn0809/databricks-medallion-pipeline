# Databricks notebook source
"""Backward-compatible entry point (delegates to validate_all)."""

from validate_all import get_spark, run_silver_pipeline

spark = get_spark()
validation_results = run_silver_pipeline(spark)

for table_name, row_count in validation_results.items():
    print(f"{table_name}: {row_count} rows written")

print("Silver pipeline complete.")
