"""Tests for dark mode theme."""

import polars as pl

from finflow_sankey import FinancialSankey


def test_dark_theme():
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
        .render(title="Dark Theme", theme="dark")
    )

    assert fig is not None
    assert fig.layout.paper_bgcolor == "#0F172A"
    assert fig.layout.plot_bgcolor == "#1E293B"
