"""Data adapters for common financial data sources."""

from __future__ import annotations

from finflow_sankey.adapters.csv import (
    load_balance_sheet_csv,
    load_cash_flow_csv,
    load_income_statement_csv,
)
from finflow_sankey.adapters.dartlab import DartlabAdapter
from finflow_sankey.adapters.excel import (
    load_balance_sheet_excel,
    load_cash_flow_excel,
    load_income_statement_excel,
)

__all__ = [
    "load_income_statement_csv",
    "load_cash_flow_csv",
    "load_balance_sheet_csv",
    "load_income_statement_excel",
    "load_cash_flow_excel",
    "load_balance_sheet_excel",
    "DartlabAdapter",
]
