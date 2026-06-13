# Quickstart

## Income Statement

```python
import polars as pl
from finflow_sankey import FinancialSankey

df = pl.DataFrame({
    "account": ["Revenue", "Cost of Revenue", "Operating Expenses", "Tax", "Net Income"],
    "value": [100.0, -40.0, -30.0, -10.0, 20.0],
    "period": ["FY2025"] * 5,
    "currency": ["USD"] * 5,
    "statement": ["income_statement"] * 5,
    "section": ["revenue", "cost_of_revenue", "operating_expenses", "tax", "profit"],
})

fig = (
    FinancialSankey
    .income_statement(df, period="FY2025", currency="USD")
    .validate()
    .render(title="FY2025 Income Statement")
)
fig.show()
```

## Cash Flow Statement

```python
fig = (
    FinancialSankey
    .cash_flow_statement(df, period="FY2025", currency="USD")
    .validate()
    .render(title="FY2025 Cash Flow Bridge")
)
```

## Balance Sheet Reconciliation

```python
fig = (
    FinancialSankey
    .balance_sheet_reconciliation(df, as_of="2025-12-31", currency="USD")
    .validate()
    .render(title="Balance Sheet")
)
```

## Export HTML

```python
FinancialSankey.income_statement(df).validate().export_html("output.html")
```
