# Retail Business Intelligence Data Mart

A reproducible retail analytics portfolio project by Felly Akili Baluku.
It validates sales data, generates a MySQL star schema load, and produces SQL KPIs and Python charts.

## Dataset and verified results

The supplied sample contains 10 sales lines, 51 units and five cities, from 5 to 10 January 2026.
Revenue after discounts is 1,024, merchandise cost is 781, and gross profit is 243.
Currency and data provenance have not been supplied. Do not interpret these amounts as a specific currency.
The source is a demonstration-sized sample. One observed month cannot support an evaluated monthly forecast.

## Run locally

Requires Python 3.10+ and MySQL 8.0.16+ with InnoDB and strict SQL mode.
From the repository root, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python python/import_sales.py
python python/sales_forecasting.py
mysql -u YOUR_USER -p
```

In the MySQL client, use a dedicated project database:

```sql
CREATE DATABASE sales_datamart CHARACTER SET utf8mb4;
USE sales_datamart;
SOURCE database/schema.sql;
SOURCE outputs/load_sales.sql;
SOURCE database/kpi_queries.sql;
```

Run from the repository directory. The import generator also accepts `--input PATH --output PATH`.
The chart script accepts `--input PATH --output-dir PATH`. Defaults are resolved relative to the repository.
The schema is for a new database. An existing incompatible schema requires a reviewed migration.

## Model and loading

The grain is one source sales line, identified by `sale_id`. This identifier must remain unique across files.
Dimensions are customer, product (name and category), store (name and city), and date.
Customer segment and payment method stay on the sales line to preserve their transaction-time values.
The importer normalizes store and city capitalization and preserves the original source file.
It validates the entire input before generating SQL. Amounts use decimal arithmetic.
A single transaction loads dimensions and facts. Replaying a sale ID updates that sales line,
so corrected source records replace earlier values without duplicating revenue.
Use one loader at a time. On a SQL error, issue `ROLLBACK` and resolve it before retrying.
Never use a client option that continues through errors to commit a partially failed load.

## Data dictionary

| Source column | Meaning |
| --- | --- |
| sale_id | Unique sales-line identifier; not necessarily an invoice number |
| date | Day/month/year |
| product, category | Product description and category |
| customer-id, customer-segment | Customer identifier and segment at sale time |
| store, city | Store description and city |
| quantity | Positive integer units |
| unit-price, unit_cost | Nonnegative unit selling price and merchandise cost |
| discount | Absolute discount for the whole line, inferred from supplied arithmetic |
| total_amount | quantity × unit-price − discount |
| cost_price | quantity × unit_cost |
| profit | Gross profit, total_amount − cost_price; operating expenses excluded |
| payment-method | Source payment label |
| month, year | Calendar attributes validated against date |
| day-of-week | Sunday=1 through Saturday=7 |

UTF-8 and Windows-1252 inputs are supported, with semicolon, tab or comma delimiters.
Fully empty rows are ignored. Duplicate identifiers, invalid calendar attributes and inconsistent amounts are rejected.

## Analytics and limitations

SQL reports cover revenue, gross profit, units, products, cities, customer segments and payment methods.
Python exports monthly revenue and payment-method charts to `outputs/`.
Forecasting requires at least 12 consecutive observed months and confirmed source coverage.
When eligible, a last-value baseline uses a three-month holdout, reports MAE and exports six future months.
Missing months remain missing. Source coverage still needs human confirmation, including completeness of boundary months.
Excel and Power BI workbooks are not included. Existing images and screenshots are historical project evidence;
regenerate current results using the scripts. No automated MySQL integration check has yet been run in the development environment.
