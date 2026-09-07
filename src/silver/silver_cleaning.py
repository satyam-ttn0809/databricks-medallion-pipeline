"""Approved Silver cleaning transformations.

Per data-quality-strategy.md and design-notes.md:
- Business values are NOT corrected (no NULL imputation, FK repair, or enum replacement).
- Bronze business columns are preserved; cleaning enforces quality through validation flags.
- Duplicate PK handling (GA-5) is applied during validation, not by deleting rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def clean_customers(df: DataFrame) -> DataFrame:
    """Prepare customers for validation. No business corrections are defined in spec."""
    return df


def clean_orders(df: DataFrame) -> DataFrame:
    """Prepare orders for validation. No business corrections are defined in spec."""
    return df


def clean_products(df: DataFrame) -> DataFrame:
    """Prepare products for validation. No business corrections are defined in spec."""
    return df
