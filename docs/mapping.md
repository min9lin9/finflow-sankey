# Account Mapping Guide

FinFlow Sankey expects your input data to use standard `section` names. If your raw data uses different account names, use the `mapping` parameter.

## Input Columns

Your DataFrame must have these exact columns:

| Column | Description |
|--------|-------------|
| `account` | Display name for the node. |
| `value` | Signed numeric value. Expenses/costs are usually negative. |
| `period` | Period label, e.g. `FY2025`. |
| `currency` | Currency label, e.g. `USD`, `KRW bn`. |
| `statement` | `income_statement`, `cash_flow_statement`, or `balance_sheet`. |
| `section` | Standard section name (see below). |

## Section Names

### Income Statement

| Section | Meaning |
|---------|---------|
| `revenue` | Total revenue |
| `cost_of_revenue` | Cost of goods sold |
| `cost` | Alias for cost_of_revenue |
| `operating_expenses` | SG&A, R&D, etc. |
| `expense` | Alias for operating_expenses |
| `tax` | Income tax expense |
| `non_operating_items` | Non-operating income or expense |
| `profit` | Net income |

### Cash Flow Statement

| Section | Meaning |
|---------|---------|
| `beginning_cash` | Starting cash balance |
| `operating_cash_flow` | Cash from operations |
| `investing_cash_flow` | Cash used in investing |
| `financing_cash_flow` | Cash from/used in financing |
| `fx_effect` | Foreign exchange effect |
| `ending_cash` | Ending cash balance |

### Balance Sheet

| Section | Meaning |
|---------|---------|
| `asset` | Total assets |
| `current_asset` | Current assets |
| `non_current_asset` | Non-current assets |
| `liability` | Total liabilities |
| `current_liability` | Current liabilities |
| `non_current_liability` | Non-current liabilities |
| `equity` | Shareholders' equity |

## Dict Mapping

```python
mapping = {
    "revenue": ["Net Sales", "Sales Revenue"],
    "cost_of_revenue": ["COGS", "Cost of Goods Sold"],
    "operating_expenses": ["SG&A", "R&D", "Selling General and Administrative"],
    "tax": ["Income Tax Expense"],
    "profit": ["Net Income", "Net Profit"],
}

FinancialSankey.income_statement(df, mapping=mapping).validate().render()
```

## YAML Mapping

Create `mapping.yaml`:

```yaml
revenue:
  - Net Sales
  - Sales Revenue
cost_of_revenue:
  - COGS
  - Cost of Goods Sold
operating_expenses:
  - SG&A
  - R&D
tax:
  - Income Tax Expense
profit:
  - Net Income
```

Use it:

```python
FinancialSankey.income_statement(df, mapping="mapping.yaml").validate().render()
```

## Mapping Precedence

1. Explicit `section` column in input data
2. `mapping` parameter (dict, YAML, or `AccountMapper`)
3. Account names that already match standard section names

If an account cannot be mapped, the validator will raise an error.
