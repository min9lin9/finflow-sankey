"""Tests for minor grouping."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey


def test_group_minor_by_top_n():
    df = pl.DataFrame({
        "account": ["Revenue", "Cost A", "Cost B", "Cost C", "Net Income"],
        "value": [100.0, -30.0, -20.0, -5.0, 45.0],
        "period": ["FY2025"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["income_statement"] * 5,
        "section": ["revenue", "cost", "cost", "cost", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .group_minor(top_n=2, label="Other")
        .render(title="Grouped")
    )

    assert fig is not None


def test_group_minor_by_min_pct():
    df = pl.DataFrame({
        "account": ["Revenue", "Cost A", "Cost B", "Cost C", "Net Income"],
        "value": [100.0, -30.0, -20.0, -5.0, 45.0],
        "period": ["FY2025"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["income_statement"] * 5,
        "section": ["revenue", "cost", "cost", "cost", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .group_minor(min_pct=0.1, label="Other")
        .render(title="Grouped by pct")
    )

    assert fig is not None


def test_group_minor_invalid_top_n():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    with pytest.raises(ValueError):
        (
            FinancialSankey
            .income_statement(df)
            .validate()
            .group_minor(top_n=0)
        )
