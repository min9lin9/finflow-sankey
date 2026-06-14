# Data Adapters

FinFlow Sankey provides adapter helpers to load data from common sources.

## CSV

```python
from finflow_sankey.adapters import load_income_statement_csv

df = load_income_statement_csv(
    "income_statement.csv",
    period="FY2025",
    currency="USD",
)
```

CSV files must contain at least these columns:

- `account`
- `value`
- `section`

The adapter adds `period`, `currency`, and `statement` columns.

## Excel

```python
from finflow_sankey.adapters import load_income_statement_excel

df = load_income_statement_excel(
    "financial_statements.xlsx",
    sheet_name="IS",
    period="FY2025",
    currency="USD",
)
```

## Dartlab CLI

```python
from finflow_sankey.adapters import DartlabAdapter

adapter = DartlabAdapter("005930")
df = adapter.load_income_statement()
```

## DART OpenAPI (dart-fss)

```python
from finflow_sankey.adapters.dart_fss import DartFssAdapter

adapter = DartFssAdapter(corp_code="00126380")
df = adapter.load_income_statement()
```

Requirements:

- `pip install dart-fss`
- `DART_API_KEY` environment variable

Get a free API key at [https://opendart.fss.or.kr](https://opendart.fss.or.kr).

## Section Mapping

If your source uses non-standard section names, pass a mapping:

```python
df = load_income_statement_csv(
    "data.csv",
    period="FY2025",
    currency="USD",
    section_mapping={"Sales": "revenue", "OpEx": "operating_expenses"},
)
```
