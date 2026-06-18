# Frequently Asked Questions

## General

### What Python versions are supported?

Python 3.9, 3.10, 3.11, and 3.12.

### Do I need pandas?

No. FinFlow Sankey is Polars-first. Input must be a `polars.DataFrame` or `polars.LazyFrame`.

### Can I use this in Jupyter?

Yes. `render()` returns a Plotly `Figure`, which renders inline in Jupyter.

```python
fig = FinancialSankey.income_statement(df).validate().render()
fig.show()
```

## Data

### What if my data has positive expenses?

Use `value` with the natural accounting sign: revenue positive, expenses negative. FinFlow's `SignNormalizer` converts expenses to positive Sankey widths internally.

### Can I load data from Excel?

Yes.

```python
import polars as pl

df = pl.read_excel("data.xlsx", sheet_name="IS")
FinancialSankey.income_statement(df).validate().render()
```

### What if my account names don't match standard sections?

Use the `mapping` parameter. See [Account Mapping](mapping.md).

## Rendering

### Why does my chart look clipped?

For the standard layout, increase figure size with `render()` kwargs or use `layout="reference"`, which auto-calculates height.

### How do I change colors?

Use a built-in theme:

```python
.render(theme="dark")
```

Or override specific roles:

```python
.render(palette={"revenue": "#0055FF", "profit": "#00AA55"})
```

### How do I export to HTML?

```python
FinancialSankey.income_statement(df).validate().export_html("output.html", title="IS")
```

## Errors

### `ValidationError: profit reconciliation failed`

Your revenue + expenses does not equal profit within the tolerance. Check:

- Expense signs (should be negative)
- Missing sections
- Currency/unit consistency

### `Missing required role colors`

Your custom palette is missing required role colors. Include at least `revenue`, `operating_expenses`, `profit`, `other`.

## Real-World Data

### Can I use DART data?

Yes. See:

- `examples/dartlab_integration.py` for summary data via Dartlab CLI
- `examples/dart_fss_integration.py` for detailed data via DART OpenAPI (`dart-fss`)

DART OpenAPI requires a free API key from https://opendart.fss.or.kr.
