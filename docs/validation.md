# Validation

FinFlow Sankey validates financial data before rendering.

## Checks

| Check | Error |
|-------|-------|
| Required columns missing | `SchemaError` |
| Multiple periods | `PeriodMismatchError` |
| Multiple currencies | `CurrencyMismatchError` |
| Duplicate accounts | `DuplicateAccountError` |
| Null values | `NullValueError` |
| Missing required accounts | `MissingAccountError` |
| Income statement reconciliation | `ReconciliationError` |
| Cash flow reconciliation | `ReconciliationError` |
| Balance sheet equation | `ReconciliationError` |

## Error Messages

Errors include structured fields such as `expected`, `actual`, `difference`, `period`, and `currency`.
