# API Reference

## Main Entry Point

### `FinancialSankey`

::: finflow_sankey.FinancialSankey
    options:
      members:
        - income_statement
        - cash_flow_statement
        - balance_sheet_reconciliation
        - multi_period_compare

## Pipeline

### `SankeyPipeline`

::: finflow_sankey.core.pipeline.SankeyPipeline
    options:
      members:
        - validate
        - group_minor
        - with_palette
        - render
        - export_html

## Core Components

### `ColorPalette`

::: finflow_sankey.core.palette.ColorPalette
    options:
      members:
        - from_yaml
        - from_dict
        - override
        - validate
        - get_role_color

### `AccountMapper`

::: finflow_sankey.core.mapper.AccountMapper
    options:
      members:
        - from_dict
        - from_yaml
        - apply
