"""Tests for pandas optional adapter."""

import pandas as pd
import polars as pl

from finflow_sankey import FinancialSankey


def test_pandas_input():
    pdf = pd.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(pdf)
        .validate()
        .render(title="Pandas Input")
    )

    assert fig is not None


def test_polars_input_still_works():
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
        .render(title="Polars Input")
    )

    assert fig is not None
