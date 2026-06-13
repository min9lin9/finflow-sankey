"""Basic tests for FinFlow Sankey."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import MissingColumnError


def test_income_statement_sankey():
    df = pl.DataFrame({
        "account": ["Revenue", "Cost of Revenue", "Operating Expenses", "Tax", "Net Income"],
        "value": [100.0, -40.0, -30.0, -10.0, 20.0],
        "period": ["FY2025"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["income_statement"] * 5,
        "section": ["revenue", "cost", "expense", "tax", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="Test Income Statement")
    )

    assert fig is not None
    assert hasattr(fig, "data")
    assert len(fig.data) == 1


def test_missing_column():
    df = pl.DataFrame({
        "account": ["Revenue"],
        "value": [100.0],
    })

    with pytest.raises(MissingColumnError):
        FinancialSankey.income_statement(df).validate()


def test_custom_palette():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .render(
            title="Custom Palette",
            palette={"revenue": "#FF0000", "profit": "#00FF00"},
        )
    )

    assert fig is not None


def test_theme():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .render(title="Colorblind Theme", theme="colorblind_safe")
    )

    assert fig is not None
