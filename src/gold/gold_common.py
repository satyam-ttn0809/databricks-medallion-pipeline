"""Shared Gold layer paths and I/O utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)

SILVER_OUTPUT_PATH = "/Volumes/ai-data_assesment/data-location/silver"
GOLD_OUTPUT_PATH = "/Volumes/ai-data_assesment/data-location/gold"


def get_spark() -> SparkSession:
    from pyspark.sql import SparkSession

    session = SparkSession.getActiveSession()
    if session is None:
        session = SparkSession.builder.getOrCreate()
    return session


def _silver_path(table_name: str) -> str:
    return f"{SILVER_OUTPUT_PATH.rstrip('/')}/{table_name}"


def _gold_path(table_name: str) -> str:
    return f"{GOLD_OUTPUT_PATH.rstrip('/')}/{table_name}"


def _check_path_exists(path: str) -> None:
    try:
        dbutils.fs.ls(path)  # type: ignore[name-defined]  # noqa: F821
    except NameError as exc:
        raise RuntimeError(
            "dbutils is required to verify table paths on Databricks."
        ) from exc
    except Exception as exc:
        raise FileNotFoundError(f"Path not found: {path}") from exc


def read_silver(spark: SparkSession, table_name: str) -> DataFrame:
    path = _silver_path(table_name)
    logger.info("Reading Silver table from %s", path)
    _check_path_exists(path)
    return spark.read.format("delta").load(path)


def write_gold(df: DataFrame, table_name: str) -> int:
    path = _gold_path(table_name)
    row_count = df.count()
    logger.info("Writing Gold table %s (%s rows) to %s", table_name, row_count, path)
    df.write.format("delta").mode("overwrite").save(path)
    return row_count
