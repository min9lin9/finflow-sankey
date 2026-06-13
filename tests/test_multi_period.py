"""Tests for multi-period comparison Sankey."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import PeriodMismatchError


def test_multi_period_comparison():
    df = pl.DataFrame({
        "account": ["Revenue", "Revenue", "Operating Expenses", "Operating Expenses"],
        "value": [100.0, 120.0, -40.0, -50.0],
        "period": ["FY2024", "FY2025", "FY2024", "FY2025"],
        "currency": ["USD"] * 4,
        "statement": ["income_statement"] * 4,
        "section": ["revenue", "revenue", "expense", "expense"],
    })

    fig = (
        FinancialSankey
        .multi_period_compare(df, currency="USD")
        .validate()
        .render(title="YoY Comparison")
    )

    assert fig is not None
    sankey = fig.data[0]
    assert len(sankey.node.label) == 4  # 2 sections x 2 periods


def test_multi_period_requires_two_periods():
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses"],
        "value": [100.0, -40.0],
        "period": ["FY2025", "FY2025"],
        "currency": ["USD"] * 2,
        "statement": ["income_statement"] * 2,
        "section": ["revenue", "expense"],
    })

    with pytest.raises(PeriodMismatchError):
        FinancialSankey.multi_period_compare(df).validate()
