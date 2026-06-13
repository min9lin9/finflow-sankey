"""Edge case tests for FinFlow Sankey validation."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import (
    CurrencyMismatchError,
    DuplicateAccountError,
    MissingAccountError,
    NullValueError,
    PeriodMismatchError,
    ReconciliationError,
)


def test_multi_period_error():
    df = pl.DataFrame({
        "account": ["Revenue", "Revenue"],
        "value": [100.0, 110.0],
        "period": ["FY2024", "FY2025"],
        "currency": ["USD"] * 2,
        "statement": ["income_statement"] * 2,
        "section": ["revenue", "revenue"],
    })

    with pytest.raises(PeriodMismatchError):
        FinancialSankey.income_statement(df).validate()


def test_multi_currency_error():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses"],
        "value": [100.0, -40.0],
        "period": ["FY2025"] * 2,
        "currency": ["USD", "KRW"],
        "statement": ["income_statement"] * 2,
        "section": ["revenue", "expense"],
    })

    with pytest.raises(CurrencyMismatchError):
        FinancialSankey.income_statement(df).validate()


def test_null_value_error():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses"],
        "value": [100.0, None],
        "period": ["FY2025"] * 2,
        "currency": ["USD"] * 2,
        "statement": ["income_statement"] * 2,
        "section": ["revenue", "expense"],
    })

    with pytest.raises(NullValueError):
        FinancialSankey.income_statement(df).validate()


def test_duplicate_account_error():
    df = pl.DataFrame({
        "account": ["Revenue", "Revenue"],
        "value": [100.0, 10.0],
        "period": ["FY2025"] * 2,
        "currency": ["USD"] * 2,
        "statement": ["income_statement"] * 2,
        "section": ["revenue", "revenue"],
    })

    with pytest.raises(DuplicateAccountError):
        FinancialSankey.income_statement(df).validate()


def test_missing_revenue_error():
    df = pl.DataFrame({
        "account": ["Operating Expenses", "Net Income"],
        "value": [-40.0, 60.0],
        "period": ["FY2025"] * 2,
        "currency": ["USD"] * 2,
        "statement": ["income_statement"] * 2,
        "section": ["expense", "profit"],
    })

    with pytest.raises(MissingAccountError):
        FinancialSankey.income_statement(df).validate()


def test_income_reconciliation_error():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 70.0],  # wrong profit
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    with pytest.raises(ReconciliationError):
        FinancialSankey.income_statement(df).validate()


def test_cash_flow_reconciliation_error():
    df = pl.DataFrame({
        "account": ["Beginning Cash", "Operating Cash Flow", "Ending Cash"],
        "value": [100.0, 30.0, 200.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["cash_flow_statement"] * 3,
        "section": ["beginning_cash", "operating_cash_flow", "ending_cash"],
    })

    with pytest.raises(ReconciliationError):
        FinancialSankey.cash_flow_statement(df).validate()
