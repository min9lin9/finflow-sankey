# API Reference

## `FinancialSankey`

Main entry point.

### `income_statement(data, *, period=None, currency=None, mapping=None)`

Create an income statement Sankey pipeline.

### `cash_flow_statement(data, *, period=None, currency=None, mapping=None)`

Create a cash flow statement Sankey pipeline.

### `balance_sheet_reconciliation(data, *, as_of=None, currency=None, mapping=None)`

Create a balance sheet reconciliation Sankey pipeline.

### `multi_period_compare(data, *, currency=None, mapping=None)`

Create a multi-period comparison Sankey pipeline. Requires exactly two distinct periods in the data.

## `SankeyPipeline`

### `.validate(tolerance=0.01)`

Validate the input data.

### `.group_minor(min_pct=None, min_value=None, top_n=None, label="Other")`

Group minor accounts into an "Other" bucket.

### `.render(title=None, renderer="plotly", palette=None, theme=None)`

Render the Sankey diagram and return a Plotly Figure.

### `.export_html(path, title=None, ...)`

Render and save the diagram to an HTML file.
