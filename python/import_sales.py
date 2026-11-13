"""Validate sales and generate a transactional MySQL load file."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONEY_FIELDS = ("unit-price", "discount", "unit_cost", "total_amount", "cost_price", "profit")
TEXT_FIELDS = ("product", "category", "customer-id", "customer-segment", "store", "city", "payment-method")
REQUIRED = {"sale_id", "date", "quantity", "month", "year", "day-of-week", *MONEY_FIELDS, *TEXT_FIELDS}


def read_sales(path):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    dialect = csv.Sniffer().sniff(text[:8192], delimiters=";\t,")
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    if not REQUIRED.issubset(reader.fieldnames or []):
        raise ValueError("Missing required CSV columns")
    sales = []
    identifiers = set()
    for line, row in enumerate(reader, start=2):
        if not any(value and value.strip() for value in row.values() if isinstance(value, str)):
            continue
        try:
            if None in row or any(row[key] is None for key in REQUIRED):
                raise ValueError("Malformed row")
            row = {key: value.strip() for key, value in row.items()}
            for key in TEXT_FIELDS:
                if not row[key]:
                    raise ValueError(f"Empty {key}")
            for key in ("sale_id", "quantity", "month", "year", "day-of-week"):
                row[key] = int(row[key])
            if row["sale_id"] <= 0 or row["quantity"] <= 0:
                raise ValueError("Identifiers and quantities must be positive")
            if row["sale_id"] in identifiers:
                raise ValueError("Duplicate sale_id")
            row["date"] = datetime.strptime(row["date"], "%d/%m/%Y").date()
            date = row["date"]
            if (row["month"], row["year"], row["day-of-week"]) != (date.month, date.year, (date.weekday() + 1) % 7 + 1):
                raise ValueError("Calendar attributes do not match date")
            for key in MONEY_FIELDS:
                value = Decimal(row[key])
                if not value.is_finite() or value != value.quantize(Decimal("0.01")) or abs(value) >= Decimal("1000000000000"):
                    raise ValueError(f"Invalid amount: {key}")
                row[key] = value
            if any(row[key] < 0 for key in ("unit-price", "discount", "unit_cost", "total_amount")):
                raise ValueError("Negative price, discount or revenue")
            if row["total_amount"] != row["quantity"] * row["unit-price"] - row["discount"]:
                raise ValueError("Revenue mismatch")
            if row["cost_price"] != row["quantity"] * row["unit_cost"] or row["profit"] != row["total_amount"] - row["cost_price"]:
                raise ValueError("Cost or gross profit mismatch")
            identifiers.add(row["sale_id"])
            sales.append(row)
        except (ValueError, InvalidOperation) as error:
            raise ValueError(f"Line {line}: {error}") from error
    if not sales:
        raise ValueError("No sales found")
    return sales


def sql_text(value):
    # Hex literals preserve Unicode and avoid SQL-mode-dependent escaping.
    return "CONVERT(X'" + value.encode("utf-8").hex() + "' USING utf8mb4)"


def make_load(sales):
    statements = ["SET NAMES utf8mb4;", "START TRANSACTION;"]
    for row in sales:
        customer = sql_text(row["customer-id"])
        product = sql_text(row["product"])
        category = sql_text(row["category"])
        city = sql_text(row["city"].title())
        store = sql_text(row["store"].title())
        date = row["date"]
        statements.extend([
            f"INSERT INTO dim_customer VALUES ({customer}) ON DUPLICATE KEY UPDATE customer_id=customer_id;",
            f"INSERT INTO dim_product (product_name, category) VALUES ({product}, {category}) ON DUPLICATE KEY UPDATE product_id=product_id;",
            f"INSERT INTO dim_store (store_name, city) VALUES ({store}, {city}) ON DUPLICATE KEY UPDATE store_id=store_id;",
            f"INSERT INTO dim_date VALUES ('{date}', {date.year}, {date.month}, {date.isoweekday()}) ON DUPLICATE KEY UPDATE date_id=date_id;",
        ])
        values = [str(row["sale_id"]), f"'{date}'", customer,
                  f"(SELECT product_id FROM dim_product WHERE product_name={product} AND category={category})",
                  f"(SELECT store_id FROM dim_store WHERE store_name={store} AND city={city})",
                  sql_text(row["customer-segment"]), sql_text(row["payment-method"]), str(row["quantity"])]
        values.extend(str(row[key]) for key in MONEY_FIELDS)
        columns = "sale_id,date_id,customer_id,product_id,store_id,customer_segment,payment_method,quantity,unit_price,discount,unit_cost,total_amount,cost_price,profit"
        updates = ",".join(f"{column}=VALUES({column})" for column in columns.split(",")[1:])
        statements.append(f"INSERT INTO sales_fact ({columns}) VALUES ({','.join(values)}) ON DUPLICATE KEY UPDATE {updates};")
    statements.append("COMMIT;")
    return "\n".join(statements) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw-sales.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/load_sales.sql")
    args = parser.parse_args()
    sales = read_sales(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(make_load(sales), encoding="utf-8")
    print(f"Validated {len(sales)} sales. Revenue={sum(r['total_amount'] for r in sales)}, gross profit={sum(r['profit'] for r in sales)}")
    print(f"SQL load file: {args.output}")


if __name__ == "__main__":
    main()
