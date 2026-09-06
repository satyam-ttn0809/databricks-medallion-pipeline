"""Shared Silver layer paths and I/O utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)

CATALOG = "ai-assesment-medillion-structure"
BRONZE_SCHEMA = "bronze"
SILVER_OUTPUT_PATH = "/Volumes/ai-data_assesment/data-location/silver"


def get_spark() -> SparkSession:
    from pyspark.sql import SparkSession

    session = SparkSession.getActiveSession()
    if session is None:
        session = SparkSession.builder.getOrCreate()
    return session


def bronze_table_name(table_name: str) -> str:
    return f"{CATALOG}.{BRONZE_SCHEMA}.{table_name}"


def _silver_path(table_name: str) -> str:
    return f"{SILVER_OUTPUT_PATH.rstrip('/')}/{table_name}"


def _get_dbutils(spark: SparkSession):
    """Return dbutils in notebooks and Python job tasks."""
    try:
        from pyspark.dbutils import DBUtils

        return DBUtils(spark)
    except ImportError:
        import IPython

        return IPython.get_ipython().user_ns["dbutils"]


def _check_path_exists(spark: SparkSession, path: str) -> None:
    try:
        _get_dbutils(spark).fs.ls(path)
    except Exception as exc:
        raise FileNotFoundError(f"Path not found: {path}") from exc


def read_bronze(spark: SparkSession, table_name: str) -> DataFrame:
    target_table = bronze_table_name(table_name)
    logger.info("Reading Bronze table %s", target_table)
    if not spark.catalog.tableExists(target_table):
        raise FileNotFoundError(f"Bronze table not found: {target_table}")
    return spark.table(target_table)


def write_silver(df: DataFrame, table_name: str) -> int:
    path = _silver_path(table_name)
    row_count = df.count()
    logger.info("Writing Silver table %s (%s rows) to %s", table_name, row_count, path)
    df.write.format("delta").mode("overwrite").save(path)
    return row_count
