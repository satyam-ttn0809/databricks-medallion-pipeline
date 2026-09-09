"""Shared Silver layer paths and I/O utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)

CATALOG = "ai-assesment-medillion-structure"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"


def get_spark() -> SparkSession:
    from pyspark.sql import SparkSession

    session = SparkSession.getActiveSession()
    if session is None:
        session = SparkSession.builder.getOrCreate()
    return session


def bronze_table_name(table_name: str) -> str:
    return f"`{CATALOG}`.`{BRONZE_SCHEMA}`.`{table_name}`"


def silver_table_name(table_name: str) -> str:
    return f"`{CATALOG}`.`{SILVER_SCHEMA}`.`{table_name}`"


def read_bronze(spark: SparkSession, table_name: str) -> DataFrame:
    target_table = bronze_table_name(table_name)
    logger.info("Reading Bronze table %s", target_table)
    try:
        return spark.table(target_table)
    except Exception as exc:
        raise FileNotFoundError(f"Bronze table not found: {target_table}") from exc


def write_silver(df: DataFrame, table_name: str) -> int:
    target_table = silver_table_name(table_name)
    row_count = df.count()
    logger.info("Writing Silver table %s (%s rows)", target_table, row_count)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(
        target_table
    )
    return row_count
