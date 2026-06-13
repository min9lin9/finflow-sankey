# FinFlow Sankey

Polars-first financial statement Sankey visualization library.

## Features

- **Polars-first**: Native support for `pl.DataFrame` and `pl.LazyFrame`
- **Accounting-aware validation**: Period/currency checks, reconciliation validation
- **Role-based color palette**: Revenue, costs, profit, cash flow each have distinct colors
- **Customizable themes**: default, monochrome, colorblind-safe, minimal, dark, plus custom YAML palettes
- **Runtime palette override**: Change colors via dict or YAML without modifying source
- **Account mapping**: Map raw account names to standard sections via dict or YAML
- **Consistent line styles**: Link widths proportional to values, but stroke widths uniform
- **Node layout**: Level-based horizontal positioning, including reconciliation side-by-side view
- **Rich hover metadata**: Original accounts, validation status, period, currency
- **HTML export**: One-line export helper
- **Multi-period comparison**: Compare two periods in a single Sankey
- **Plotly renderer**: Returns `plotly.graph_objects.Figure` for Jupyter, Streamlit, Dash, HTML export

## Quickstart

```python
import polars as pl
from finflow_sankey import FinancialSankey

df = pl.DataFrame({
    "account": ["Revenue", "Cost of Revenue", "Operating Expenses", "Tax", "Net Income"],
    "value": [100_000_000.0, -40_000_000.0, -30_000_000.0, -10_000_000.0, 20_000_000.0],
    "period": ["FY2025"] * 5,
    "currency": ["USD"] * 5,
    "statement": ["income_statement"] * 5,
    "section": ["revenue", "cost_of_revenue", "operating_expenses", "tax", "profit"],
})

fig = (
    FinancialSankey
    .income_statement(df, period="FY2025", currency="USD")
    .validate()
    .render(title="FY2025 Income Statement Flow")
)

fig.show()
```

### Cash Flow Statement

```python
df = pl.DataFrame({
    "account": [
        "Beginning Cash",
        "Operating Cash Flow",
        "Investing Cash Flow",
        "Financing Cash Flow",
        "FX Effect",
        "Ending Cash",
    ],
    "value": [50_000_000.0, 25_000_000.0, -10_000_000.0, -5_000_000.0, 2_000_000.0, 62_000_000.0],
    "period": ["FY2025"] * 6,
    "currency": ["USD"] * 6,
    "statement": ["cash_flow_statement"] * 6,
    "section": [
        "beginning_cash",
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "fx_effect",
        "ending_cash",
    ],
})

fig = (
    FinancialSankey
    .cash_flow_statement(df, period="FY2025", currency="USD")
    .validate()
    .render(title="FY2025 Cash Flow Bridge")
)
```

### Balance Sheet Reconciliation

```python
df = pl.DataFrame({
    "account": [
        "Current Assets",
        "Non-current Assets",
        "Current Liabilities",
        "Non-current Liabilities",
        "Equity",
    ],
    "value": [60_000_000.0, 40_000_000.0, 30_000_000.0, 20_000_000.0, 50_000_000.0],
    "period": ["2025-12-31"] * 5,
    "currency": ["USD"] * 5,
    "statement": ["balance_sheet"] * 5,
    "section": [
        "current_asset",
        "non_current_asset",
        "current_liability",
        "non_current_liability",
        "equity",
    ],
})

fig = (
    FinancialSankey
    .balance_sheet_reconciliation(df, as_of="2025-12-31", currency="USD")
    .validate()
    .render(title="Balance Sheet Reconciliation")
)
```

### Multi-Period Comparison

```python
df = pl.DataFrame({
    "account": ["Revenue", "Revenue", "Operating Expenses", "Operating Expenses"],
    "value": [100_000_000.0, 120_000_000.0, -40_000_000.0, -50_000_000.0],
    "period": ["FY2024", "FY2025", "FY2024", "FY2025"],
    "currency": ["USD"] * 4,
    "statement": ["income_statement"] * 4,
    "section": ["revenue", "revenue", "expense", "expense"],
})

fig = (
    FinancialSankey
    .multi_period_compare(df, currency="USD")
    .validate()
    .render(title="FY2024 vs FY2025")
)
```

## Account Mapping

Map raw account names to standard sections via dict or YAML:

```python
mapping = {
    "revenue": ["Net Sales", "Sales Revenue"],
    "cost_of_revenue": ["COGS", "Cost of Goods Sold"],
    "operating_expenses": ["SG&A", "R&D"],
    "tax": ["Income Tax Expense"],
    "profit": ["Net Income"],
}

fig = FinancialSankey.income_statement(df, mapping=mapping).validate().render()
```

## Themes & Palettes

```python
# Built-in theme
fig = FinancialSankey.income_statement(df).validate().render(theme="colorblind_safe")

# Dark mode
fig = FinancialSankey.income_statement(df).validate().render(theme="dark")

# Custom YAML palette
fig = FinancialSankey.income_statement(df).validate().render(palette="./my_palette.yaml")

# Runtime dict override
fig = FinancialSankey.income_statement(df).validate().render(
    palette={"revenue": "#0055FF", "profit": "#00AA55"}
)
```

## HTML Export

```python
(
    FinancialSankey
    .income_statement(df)
    .validate()
    .export_html("income_statement.html", title="FY2025 Income Statement")
)
```

## Installation

```bash
pip install -e ".[dev]"
```

## Development

```bash
python -m pytest tests/ -v
ruff check finflow_sankey tests
```

## Project Structure

```
finflow_sankey/
  core/           # schema, validation, normalization, graph, palette, mapper
  templates/      # income_statement, cash_flow, balance_sheet, multi_period
  renderers/      # plotly renderer
  palettes/       # YAML color palettes
  mappings/       # YAML account mappings
  adapters/       # pandas adapter
  examples/       # usage examples
tests/            # pytest suite
```

## License

MIT
