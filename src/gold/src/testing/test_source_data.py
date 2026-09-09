"""AC-1 / AC-2: Validate source CSV row counts and intentional defect counts.

Runs without Spark (design-notes.md Testing Strategy — data generation counts).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "data_generation"))

from generate_sample_data import validate_generated_data  # noqa: E402

DATA_DIR = REPO_ROOT / "data"


def test_source_data_matches_spec() -> None:
    result = validate_generated_data(DATA_DIR)
    assert result.passed, f"Source data validation failed: {result.details}"
    expected = result.details["expected"]
    assert expected["null_emails"] == 50
    assert expected["duplicate_customer_rows"] == 10
    assert expected["null_customer_ids"] == 100
    assert expected["null_product_ids"] == 200
    assert expected["invalid_customer_fks"] == 50
    assert expected["invalid_product_fks"] == 30
    assert expected["duplicate_order_rows"] == 20
    assert all(result.details["type_checks"].values())


if __name__ == "__main__":
    test_source_data_matches_spec()
    print("test_source_data: PASSED")
