"""Silver processing pipeline: clean -> validate -> write."""

from __future__ import annotations

from typing import TYPE_CHECKING

from quality_checks import validate_customers, validate_orders, validate_products
from silver_cleaning import clean_customers, clean_orders, clean_products

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def process_customers(bronze_df: DataFrame) -> DataFrame:
    return validate_customers(clean_customers(bronze_df))


def process_orders(
    bronze_df: DataFrame,
    bronze_customers: DataFrame,
    bronze_products: DataFrame,
) -> DataFrame:
    return validate_orders(
        clean_orders(bronze_df),
        bronze_customers.select("customer_id"),
        bronze_products.select("product_id"),
    )


def process_products(bronze_df: DataFrame) -> DataFrame:
    return validate_products(clean_products(bronze_df))
