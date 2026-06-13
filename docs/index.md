# FinFlow Sankey

Polars-first financial statement Sankey visualization library.

## What is FinFlow Sankey?

FinFlow Sankey converts financial statement data into accounting-validated Sankey diagrams.

```text
Revenue → Cost of Revenue / Gross Profit → Operating Expenses / Operating Income → Tax / Net Income
```

## Key Features

- **Polars-first**: Native `pl.DataFrame` and `pl.LazyFrame` support.
- **Accounting validation**: Detects period/currency mismatches and reconciliation errors before rendering.
- **Role-based colors**: Revenue, costs, profit, cash flows each have distinct colors.
- **Customizable themes**: Built-in themes plus YAML/dict palette overrides.
- **Multiple statements**: Income statement, cash flow statement, balance sheet reconciliation, and multi-period comparison.
- **Plotly output**: Returns `plotly.graph_objects.Figure` for Jupyter, Streamlit, Dash, or HTML export.

## Installation

```bash
pip install finflow-sankey
```

## Quick Example

```python
import polars as pl
from finflow_sankey import FinancialSankey

df = pl.DataFrame({
    "account": ["Revenue", "Operating Expenses", "Net Income"],
    "value": [100.0, -40.0, 60.0],
    "period": ["FY2025"] * 3,
    "currency": ["USD"] * 3,
    "statement": ["income_statement"] * 3,
    "section": ["revenue", "expense", "profit"],
})

fig = FinancialSankey.income_statement(df).validate().render()
fig.show()
```
