"""Tests for cash flow statement Sankey."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import ReconciliationError


def test_cash_flow_sankey():
    df = pl.DataFrame({
        "account": [
            "Beginning Cash",
            "Operating Cash Flow",
            "Investing Cash Flow",
            "Financing Cash Flow",
            "FX Effect",
            "Ending Cash",
        ],
        "value": [100.0, 30.0, -20.0, -10.0, 5.0, 105.0],
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
        .render(title="Test Cash Flow")
    )

    assert fig is not None
    assert hasattr(fig, "data")
    assert len(fig.data) == 1


def test_cash_flow_reconciliation_error():
    df = pl.DataFrame({
        "account": [
            "Beginning Cash",
            "Operating Cash Flow",
            "Ending Cash",
        ],
        "value": [100.0, 30.0, 200.0],  # wrong ending cash
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["cash_flow_statement"] * 3,
        "section": [
            "beginning_cash",
            "operating_cash_flow",
            "ending_cash",
        ],
    })

    with pytest.raises(ReconciliationError):
        FinancialSankey.cash_flow_statement(df).validate()


def test_cash_flow_custom_theme():
    df = pl.DataFrame({
        "account": [
            "Beginning Cash",
            "Operating Cash Flow",
            "Investing Cash Flow",
            "Ending Cash",
        ],
        "value": [100.0, 30.0, -20.0, 110.0],
        "period": ["FY2025"] * 4,
        "currency": ["USD"] * 4,
        "statement": ["cash_flow_statement"] * 4,
        "section": [
            "beginning_cash",
            "operating_cash_flow",
            "investing_cash_flow",
            "ending_cash",
        ],
    })

    fig = (
        FinancialSankey
        .cash_flow_statement(df)
        .validate()
        .render(title="Cash Flow Minimal", theme="minimal")
    )

    assert fig is not None
