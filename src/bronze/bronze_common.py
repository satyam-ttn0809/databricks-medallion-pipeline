"""Shared Bronze ingestion utilities (schemas, paths, ingest logic)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    DecimalType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

RAW_DATA_PATH = "/Volumes/ai-data_assesment/data-location/raw-data"
BRONZE_OUTPUT_PATH = "/Volumes/ai-data_assesment/data-location/bronze"

CUSTOMERS_SCHEMA = StructType(
    [
        StructField("customer_id", IntegerType(), False),
        StructField("customer_name", StringType(), False),
        StructField("email", StringType(), True),
        StructField("country", StringType(), True),
        StructField("signup_date", DateType(), True),
        StructField("customer_segment", StringType(), True),
        StructField("lifetime_value", DecimalType(10, 2), True),
    ]
)

ORDERS_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType(), False),
        StructField("customer_id", IntegerType(), True),
        StructField("order_date", DateType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DecimalType(10, 2), True),
        StructField("total_amount", DecimalType(10, 2), True),
        StructField("order_status", StringType(), True),
        StructField("payment_date", DateType(), True),
    ]
)

PRODUCTS_SCHEMA = StructType(
    [
        StructField("product_id", IntegerType(), False),
        StructField("product_name", StringType(), True),
        StructField("category", StringType(), True),
        StructField("price", DecimalType(10, 2), True),
        StructField("cost", DecimalType(10, 2), True),
        StructField("stock_quantity", IntegerType(), True),
        StructField("reorder_level", IntegerType(), True),
    ]
)


def get_spark() -> SparkSession:
    """Return active Databricks Spark session or create one for local use."""
    from pyspark.sql import SparkSession

    session = SparkSession.getActiveSession()
    if session is None:
        session = SparkSession.builder.getOrCreate()
    return session


def _source_path(filename: str) -> str:
    return f"{RAW_DATA_PATH.rstrip('/')}/{filename}"


def _bronze_path(table_name: str) -> str:
    return f"{BRONZE_OUTPUT_PATH.rstrip('/')}/{table_name}"


def _check_source_exists(source_path: str) -> None:
    try:
        dbutils.fs.ls(source_path)  # type: ignore[name-defined]  # noqa: F821
    except NameError as exc:
        raise RuntimeError(
            "dbutils is required to verify source paths on Databricks."
        ) from exc
    except Exception as exc:
        raise FileNotFoundError(f"Source path not found: {source_path}") from exc


def ingest_csv_to_bronze(
    spark: SparkSession,
    *,
    source_filename: str,
    schema: StructType,
    table_name: str,
) -> int:
    """Read a CSV with explicit schema and write a Bronze Delta table."""
    source_path = _source_path(source_filename)
    output_path = _bronze_path(table_name)

    logger.info("Starting Bronze ingestion for %s from %s", table_name, source_path)
    _check_source_exists(source_path)

    df = (
        spark.read.option("header", True)
        .option("dateFormat", "yyyy-MM-dd")
        .schema(schema)
        .csv(source_path)
    )

    bronze_df = (
        df.withColumn("_ingestion_timestamp", F.current_timestamp())
        .withColumn("_source_file", F.lit(source_path))
    )

    row_count = bronze_df.count()
    logger.info("Bronze %s row count before write: %s", table_name, row_count)

    bronze_df.write.format("delta").mode("overwrite").save(output_path)

    logger.info(
        "Bronze ingestion complete for %s: %s rows written to %s",
        table_name,
        row_count,
        output_path,
    )
    return row_count


def ingest_customers(spark: SparkSession) -> int:
    return ingest_csv_to_bronze(
        spark,
        source_filename="customers.csv",
        schema=CUSTOMERS_SCHEMA,
        table_name="bronze_customers",
    )


def ingest_orders(spark: SparkSession) -> int:
    return ingest_csv_to_bronze(
        spark,
        source_filename="orders.csv",
        schema=ORDERS_SCHEMA,
        table_name="bronze_orders",
    )


def ingest_products(spark: SparkSession) -> int:
    return ingest_csv_to_bronze(
        spark,
        source_filename="products.csv",
        schema=PRODUCTS_SCHEMA,
        table_name="bronze_products",
    )
