"""Generate deterministic e-commerce CSV sample data with intentional quality issues.

Designed for execution on a Databricks cluster driver or notebook.
The LLM does not execute this script; the user runs it manually in Databricks.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

DEFAULT_SEED = 42
CUSTOMER_COUNT = 10_000
ORDER_COUNT = 100_000
PRODUCT_COUNT = 500

NULL_EMAIL_COUNT = 50
DUPLICATE_CUSTOMER_COUNT = 10
NULL_CUSTOMER_ID_COUNT = 100
NULL_PRODUCT_ID_COUNT = 200
INVALID_CUSTOMER_FK_COUNT = 50
INVALID_PRODUCT_FK_COUNT = 30
DUPLICATE_ORDER_COUNT = 20

SEGMENTS = ("Premium", "Standard", "Basic")
ORDER_STATUSES = ("Pending", "Completed", "Cancelled")
CATEGORIES = ("Electronics", "Clothing", "Home", "Sports", "Books")
COUNTRIES = ("US", "UK", "DE", "FR", "IN", "CA", "AU")

# Approved design (A-3): local `data/` or Databricks path via DATA_DIR env var.
DEFAULT_OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    details: dict[str, object]


def _money(value: float) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_products(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for product_id in range(1, PRODUCT_COUNT + 1):
        cost = rng.uniform(5, 200)
        price = cost * rng.uniform(1.1, 2.5)
        rows.append(
            {
                "product_id": product_id,
                "product_name": f"Product {product_id}",
                "category": rng.choice(CATEGORIES),
                "price": _money(price),
                "cost": _money(cost),
                "stock_quantity": rng.randint(0, 500),
                "reorder_level": rng.randint(10, 50),
            }
        )
    return rows


def generate_customers(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for customer_id in range(1, CUSTOMER_COUNT + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": f"Customer {customer_id}",
                "email": f"customer{customer_id}@example.com",
                "country": rng.choice(COUNTRIES),
                "signup_date": _random_date(rng, date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
                "customer_segment": rng.choice(SEGMENTS),
                "lifetime_value": _money(rng.uniform(100, 10_000)),
            }
        )
    return rows


def generate_orders(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for order_id in range(1, ORDER_COUNT + 1):
        customer_id = rng.randint(1, CUSTOMER_COUNT)
        product_id = rng.randint(1, PRODUCT_COUNT)
        quantity = rng.randint(1, 5)
        unit_price = rng.uniform(10, 500)
        total_amount = quantity * unit_price
        order_status = rng.choice(ORDER_STATUSES)
        order_date = _random_date(rng, date(2023, 1, 1), date(2025, 8, 31))
        payment_date = ""
        if order_status == "Completed":
            payment_date = (order_date + timedelta(days=rng.randint(0, 5))).isoformat()

        rows.append(
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": order_date.isoformat(),
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": _money(unit_price),
                "total_amount": _money(total_amount),
                "order_status": order_status,
                "payment_date": payment_date,
            }
        )
    return rows


def _inject_customer_defects(
    rows: list[dict[str, object]], rng: random.Random
) -> list[dict[str, object]]:
    null_indices = rng.sample(range(len(rows)), NULL_EMAIL_COUNT)
    for index in null_indices:
        rows[index]["email"] = ""

    duplicate_sources = rng.sample(range(len(rows)), DUPLICATE_CUSTOMER_COUNT)
    duplicates = [dict(rows[index]) for index in duplicate_sources]
    return rows + duplicates


def _inject_order_defects(
    rows: list[dict[str, object]], rng: random.Random
) -> list[dict[str, object]]:
    null_customer_indices = set(rng.sample(range(len(rows)), NULL_CUSTOMER_ID_COUNT))
    for index in null_customer_indices:
        rows[index]["customer_id"] = ""

    null_product_indices = set(rng.sample(range(len(rows)), NULL_PRODUCT_ID_COUNT))
    for index in null_product_indices:
        rows[index]["product_id"] = ""

    invalid_customer_candidates = [
        index for index in range(len(rows)) if index not in null_customer_indices
    ]
    for index in rng.sample(invalid_customer_candidates, INVALID_CUSTOMER_FK_COUNT):
        rows[index]["customer_id"] = CUSTOMER_COUNT + rng.randint(1, 1000)

    invalid_product_candidates = [
        index for index in range(len(rows)) if index not in null_product_indices
    ]
    for index in rng.sample(invalid_product_candidates, INVALID_PRODUCT_FK_COUNT):
        rows[index]["product_id"] = PRODUCT_COUNT + rng.randint(1, 100)

    duplicate_sources = rng.sample(range(len(rows)), DUPLICATE_ORDER_COUNT)
    duplicates = [dict(rows[index]) for index in duplicate_sources]
    return rows + duplicates


def generate_sample_data(output_dir: Path, seed: int = DEFAULT_SEED) -> dict[str, int]:
    rng = random.Random(seed)

    products = generate_products(rng)
    customers = generate_customers(rng)
    customers = _inject_customer_defects(customers, rng)
    orders = generate_orders(rng)
    orders = _inject_order_defects(orders, rng)

    _write_csv(output_dir / "products.csv", list(products[0].keys()), products)
    _write_csv(output_dir / "customers.csv", list(customers[0].keys()), customers)
    _write_csv(output_dir / "orders.csv", list(orders[0].keys()), orders)

    return {
        "products": len(products),
        "customers": len(customers),
        "orders": len(orders),
    }


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def _is_decimal(value: str) -> bool:
    try:
        Decimal(value)
        return True
    except Exception:
        return False


def _is_date(value: str) -> bool:
    if not value:
        return True
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_generated_data(output_dir: Path) -> ValidationResult:
    """Validate generated CSVs against approved row counts and defect counts."""
    customers_path = output_dir / "customers.csv"
    orders_path = output_dir / "orders.csv"
    products_path = output_dir / "products.csv"

    for path in (customers_path, orders_path, products_path):
        if not path.exists():
            return ValidationResult(False, {"error": f"Missing file: {path}"})

    customers = _read_csv(customers_path)
    orders = _read_csv(orders_path)
    products = _read_csv(products_path)

    valid_customer_ids = {row["customer_id"] for row in customers if row["customer_id"]}
    valid_product_ids = {row["product_id"] for row in products if row["product_id"]}

    customer_id_counts = Counter(row["customer_id"] for row in customers)
    order_id_counts = Counter(row["order_id"] for row in orders)

    null_emails = sum(1 for row in customers if not row["email"].strip())
    null_customer_ids = sum(1 for row in orders if not str(row["customer_id"]).strip())
    null_product_ids = sum(1 for row in orders if not str(row["product_id"]).strip())

    invalid_customer_fks = sum(
        1
        for row in orders
        if str(row["customer_id"]).strip() and row["customer_id"] not in valid_customer_ids
    )
    invalid_product_fks = sum(
        1
        for row in orders
        if str(row["product_id"]).strip() and row["product_id"] not in valid_product_ids
    )

    duplicate_customer_rows = sum(count - 1 for count in customer_id_counts.values() if count > 1)
    duplicate_order_rows = sum(count - 1 for count in order_id_counts.values() if count > 1)

    type_checks = {
        "customer_int_fields": all(_is_int(row["customer_id"]) for row in customers),
        "customer_decimal_fields": all(_is_decimal(row["lifetime_value"]) for row in customers),
        "customer_date_fields": all(_is_date(row["signup_date"]) for row in customers),
        "order_int_fields": all(
            (not str(row["customer_id"]).strip() or _is_int(row["customer_id"]))
            and (not str(row["product_id"]).strip() or _is_int(row["product_id"]))
            and _is_int(row["order_id"])
            and _is_int(row["quantity"])
            for row in orders
        ),
        "order_decimal_fields": all(
            _is_decimal(row["unit_price"]) and _is_decimal(row["total_amount"]) for row in orders
        ),
        "order_date_fields": all(
            _is_date(row["order_date"]) and _is_date(row["payment_date"]) for row in orders
        ),
        "product_int_fields": all(
            _is_int(row["product_id"])
            and _is_int(row["stock_quantity"])
            and _is_int(row["reorder_level"])
            for row in products
        ),
        "product_decimal_fields": all(
            _is_decimal(row["price"]) and _is_decimal(row["cost"]) for row in products
        ),
    }

    expected = {
        "products_rows": PRODUCT_COUNT,
        "customers_rows": CUSTOMER_COUNT + DUPLICATE_CUSTOMER_COUNT,
        "orders_rows": ORDER_COUNT + DUPLICATE_ORDER_COUNT,
        "null_emails": NULL_EMAIL_COUNT,
        "duplicate_customer_rows": DUPLICATE_CUSTOMER_COUNT,
        "null_customer_ids": NULL_CUSTOMER_ID_COUNT,
        "null_product_ids": NULL_PRODUCT_ID_COUNT,
        "invalid_customer_fks": INVALID_CUSTOMER_FK_COUNT,
        "invalid_product_fks": INVALID_PRODUCT_FK_COUNT,
        "duplicate_order_rows": DUPLICATE_ORDER_COUNT,
    }

    actual = {
        "products_rows": len(products),
        "customers_rows": len(customers),
        "orders_rows": len(orders),
        "null_emails": null_emails,
        "duplicate_customer_rows": duplicate_customer_rows,
        "null_customer_ids": null_customer_ids,
        "null_product_ids": null_product_ids,
        "invalid_customer_fks": invalid_customer_fks,
        "invalid_product_fks": invalid_product_fks,
        "duplicate_order_rows": duplicate_order_rows,
    }

    passed = actual == expected and all(type_checks.values())
    return ValidationResult(passed=passed, details={"expected": expected, "actual": actual, "type_checks": type_checks})


def verify_reproducibility(output_dir: Path, seed: int = DEFAULT_SEED) -> bool:
    """Re-generate with the same seed and compare file contents."""
    first = generate_sample_data(output_dir, seed=seed)
    first_customers = (output_dir / "customers.csv").read_text(encoding="utf-8")
    first_orders = (output_dir / "orders.csv").read_text(encoding="utf-8")
    first_products = (output_dir / "products.csv").read_text(encoding="utf-8")

    second = generate_sample_data(output_dir, seed=seed)
    return (
        first == second
        and first_customers == (output_dir / "customers.csv").read_text(encoding="utf-8")
        and first_orders == (output_dir / "orders.csv").read_text(encoding="utf-8")
        and first_products == (output_dir / "products.csv").read_text(encoding="utf-8")
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate sample e-commerce CSV files for the medallion pipeline"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for CSV files (default: DATA_DIR env var or 'data')",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed")
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Generate files without running validation checks",
    )
    args = parser.parse_args()

    counts = generate_sample_data(args.output_dir, seed=args.seed)
    print(f"Generated CSV files in {args.output_dir}: {counts}")

    if args.skip_validation:
        return

    validation = validate_generated_data(args.output_dir)
    reproducible = verify_reproducibility(args.output_dir, seed=args.seed)

    print(f"Validation passed: {validation.passed}")
    print(f"Reproducible: {reproducible}")
    print(f"Details: {validation.details}")

    if not validation.passed or not reproducible:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
