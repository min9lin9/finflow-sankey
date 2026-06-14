# FinFlow Sankey

[![PyPI version](https://badge.fury.io/py/finflow-sankey.svg)](https://pypi.org/project/finflow-sankey/)
[![Python](https://img.shields.io/pypi/pyversions/finflow-sankey.svg)](https://pypi.org/project/finflow-sankey/)
[![Tests](https://github.com/min9lin9/finflow-sankey/actions/workflows/ci.yml/badge.svg)](https://github.com/min9lin9/finflow-sankey/actions)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://min9lin9.github.io/finflow-sankey/)

Polars-first financial statement Sankey visualization library.

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

FinancialSankey.income_statement(df, period="FY2025", currency="USD").validate().export_html(
    "income_statement.html", title="FY2025 Income Statement"
)
```

## Installation

```bash
pip install finflow-sankey
```

Requires Python 3.9 or later.

## Features

- **Polars-first**: Native `pl.DataFrame` / `pl.LazyFrame` support. No pandas required.
- **Accounting-aware validation**: Period/currency checks, reconciliation validation.
- **Role-based color palette**: Revenue, costs, profit, cash flow each have distinct colors.
- **Customizable themes**: `default`, `monochrome`, `colorblind_safe`, `minimal`, `dark`, plus custom YAML palettes.
- **Runtime palette override**: Change colors via dict or YAML without modifying source.
- **Account mapping**: Map raw account names to standard sections via dict or YAML.
- **Reference layout** (opt-in): Detailed account nodes with fixed layout for presentations.
- **HTML export**: One-line export helper.
- **Multi-period comparison**: Compare two periods in a single Sankey.

## Input Format

Your DataFrame must contain these columns:

| Column | Type | Description |
|--------|------|-------------|
| `account` | str | Account name shown on nodes. |
| `value` | float | Signed numeric value. Expenses are typically negative. |
| `period` | str | Period label (e.g. `FY2025`, `2024-12-31`). |
| `currency` | str | Currency label (e.g. `USD`, `KRW tn`). |
| `statement` | str | One of `income_statement`, `cash_flow_statement`, `balance_sheet`. |
| `section` | str | Standard section. See table below. |

### Supported Sections

| Statement | Sections |
|-----------|----------|
| Income statement | `revenue`, `cost_of_revenue`, `cost`, `expense`, `operating_expenses`, `tax`, `non_operating_items`, `profit` |
| Cash flow | `beginning_cash`, `operating_cash_flow`, `investing_cash_flow`, `financing_cash_flow`, `fx_effect`, `ending_cash` |
| Balance sheet | `asset`, `current_asset`, `non_current_asset`, `liability`, `current_liability`, `non_current_liability`, `equity` |

## Quick Examples

### Income Statement

```python
fig = FinancialSankey.income_statement(df, period="FY2025", currency="USD").validate().render(
    title="FY2025 Income Statement"
)
fig.show()
```

### Reference Layout (Detailed View)

```python
fig = FinancialSankey.income_statement(df, layout="reference").validate().render(
    title="Detailed Income Statement"
)
```

### Cash Flow Statement

```python
fig = FinancialSankey.cash_flow_statement(df_cf, period="FY2025", currency="USD").validate().render(
    title="Cash Flow Bridge"
)
```

### Balance Sheet Reconciliation

```python
fig = FinancialSankey.balance_sheet_reconciliation(df_bs, as_of="2025-12-31", currency="USD").validate().render(
    title="Balance Sheet"
)
```

### Multi-Period Comparison

```python
fig = FinancialSankey.multi_period_compare(df_multi, currency="USD").validate().render(
    title="YoY Comparison"
)
```

## Themes & Palettes

```python
# Built-in theme
fig = FinancialSankey.income_statement(df).validate().render(theme="dark")

# Custom YAML palette
fig = FinancialSankey.income_statement(df).validate().render(palette="./my_palette.yaml")

# Runtime dict override
fig = FinancialSankey.income_statement(df).validate().render(
    palette={"revenue": "#0055FF", "profit": "#00AA55"}
)
```

## Account Mapping

Map raw account names to standard sections when your data uses different labels:

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

## HTML Export

```python
FinancialSankey.income_statement(df).validate().export_html(
    "income_statement.html", title="FY2025 Income Statement"
)
```

## Real-World Data

See [`examples/dartlab_integration.py`](examples/dartlab_integration.py) for fetching live Samsung Electronics data via [Dartlab CLI](https://github.com/eddmpython/dartlab).

## Documentation

Full documentation is available at [https://min9lin9.github.io/finflow-sankey/](https://min9lin9.github.io/finflow-sankey/).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and the path to v1.0.

## Community

- [GitHub Discussions](https://github.com/min9lin9/finflow-sankey/discussions) for questions and usage help
- [Issue Templates](https://github.com/min9lin9/finflow-sankey/issues/new/choose) for bugs and feature requests
- [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
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
  examples/       # usage examples
tests/            # pytest suite
docs/             # mkdocs documentation
```

## License

MIT
