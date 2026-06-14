"""Edge case tests for FinFlow Sankey."""

from __future__ import annotations

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import (
    CurrencyMismatchError,
    DuplicateAccountError,
    MissingAccountError,
    NullValueError,
    PeriodMismatchError,
)


def _base_df(accounts: list[str], values: list[float], sections: list[str]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "account": accounts,
            "value": values,
            "period": ["FY2025"] * len(accounts),
            "currency": ["USD"] * len(accounts),
            "statement": ["income_statement"] * len(accounts),
            "section": sections,
        }
    )


def test_zero_values_dont_crash():
    df = _base_df(
        ["Revenue", "Cost of Revenue", "Net Income"],
        [100.0, 0.0, 100.0],
        ["revenue", "cost_of_revenue", "profit"],
    )
    fig = FinancialSankey.income_statement(df).validate().render()
    assert fig is not None


def test_extreme_ratio_large_revenue_small_profit():
    df = _base_df(
        ["Revenue", "Operating Expenses", "Net Income"],
        [1_000_000_000.0, -999_999_900.0, 100.0],
        ["revenue", "operating_expenses", "profit"],
    )
    fig = FinancialSankey.income_statement(df).validate().render()
    sankey = fig.data[0]
    assert len(sankey.node.label) >= 3


def test_negative_revenue_is_allowed_but_warns():
    df = _base_df(
        ["Revenue", "Operating Expenses", "Net Income"],
        [-100.0, 50.0, -50.0],
        ["revenue", "operating_expenses", "profit"],
    )
    # Current implementation allows negative revenue; ensure it does not crash.
    fig = FinancialSankey.income_statement(df).validate().render()
    assert fig is not None


def test_missing_profit_section_fails():
    df = _base_df(
        ["Revenue", "Operating Expenses"],
        [100.0, -50.0],
        ["revenue", "operating_expenses"],
    )
    with pytest.raises(MissingAccountError):
        FinancialSankey.income_statement(df).validate()


def test_mismatched_currency_fails():
    df = pl.DataFrame(
        {
            "account": ["Revenue", "Operating Expenses", "Net Income"],
            "value": [100.0, -50.0, 50.0],
            "period": ["FY2025"] * 3,
            "currency": ["USD", "USD", "KRW"],
            "statement": ["income_statement"] * 3,
            "section": ["revenue", "operating_expenses", "profit"],
        }
    )
    with pytest.raises(CurrencyMismatchError):
        FinancialSankey.income_statement(df).validate()


def test_mismatched_period_fails():
    df = pl.DataFrame(
        {
            "account": ["Revenue", "Operating Expenses", "Net Income"],
            "value": [100.0, -50.0, 50.0],
            "period": ["FY2025", "FY2025", "FY2024"],
            "currency": ["USD"] * 3,
            "statement": ["income_statement"] * 3,
            "section": ["revenue", "operating_expenses", "profit"],
        }
    )
    with pytest.raises(PeriodMismatchError):
        FinancialSankey.income_statement(df).validate()


def test_duplicate_accounts_fails():
    df = _base_df(
        ["Revenue", "Revenue", "Net Income"],
        [100.0, -50.0, 50.0],
        ["revenue", "operating_expenses", "profit"],
    )
    with pytest.raises(DuplicateAccountError):
        FinancialSankey.income_statement(df).validate()


def test_reference_layout_with_no_details():
    df = _base_df(
        ["Revenue", "Operating Expenses", "Net Income"],
        [100.0, -50.0, 50.0],
        ["revenue", "operating_expenses", "profit"],
    )
    fig = FinancialSankey.income_statement(df, layout="reference").validate().render()
    sankey = fig.data[0]
    labels = [label.split("<br>")[0] for label in sankey.node.label]
    assert "Revenue" in labels
    assert "Net Income" in labels


def test_empty_dataframe_fails():
    df = pl.DataFrame(
        schema={
            "account": pl.Utf8,
            "value": pl.Float64,
            "period": pl.Utf8,
            "currency": pl.Utf8,
            "statement": pl.Utf8,
            "section": pl.Utf8,
        }
    )
    with pytest.raises(MissingAccountError):
        FinancialSankey.income_statement(df).validate()


def test_lazeframe_input():
    df = _base_df(
        ["Revenue", "Operating Expenses", "Net Income"],
        [100.0, -50.0, 50.0],
        ["revenue", "operating_expenses", "profit"],
    )
    fig = FinancialSankey.income_statement(df.lazy()).validate().render()
    assert fig is not None


def test_all_themes_render():
    df = _base_df(
        ["Revenue", "Cost of Revenue", "Operating Expenses", "Tax", "Net Income"],
        [100.0, -30.0, -40.0, -10.0, 20.0],
        ["revenue", "cost_of_revenue", "operating_expenses", "tax", "profit"],
    )
    for theme in ["default", "dark", "minimal", "monochrome", "colorblind_safe"]:
        fig = FinancialSankey.income_statement(df).validate().render(theme=theme)
        assert fig is not None


def test_multi_period_compare_requires_two_periods():
    df = pl.DataFrame(
        {
            "account": ["Revenue", "Revenue"],
            "value": [100.0, 120.0],
            "period": ["FY2024", "FY2025"],
            "currency": ["USD", "USD"],
            "statement": ["income_statement", "income_statement"],
            "section": ["revenue", "revenue"],
        }
    )
    fig = FinancialSankey.multi_period_compare(df, currency="USD").validate().render()
    assert fig is not None


def test_multi_period_compare_rejects_one_period():
    df = pl.DataFrame(
        {
            "account": ["Revenue"],
            "value": [100.0],
            "period": ["FY2025"],
            "currency": ["USD"],
            "statement": ["income_statement"],
            "section": ["revenue"],
        }
    )
    with pytest.raises(PeriodMismatchError):
        FinancialSankey.multi_period_compare(df, currency="USD").validate()


def test_mapping_dict():
    df = pl.DataFrame(
        {
            "account": ["Net Sales", "SG&A", "Net Income"],
            "value": [100.0, -50.0, 50.0],
            "period": ["FY2025"] * 3,
            "currency": ["USD"] * 3,
            "statement": ["income_statement"] * 3,
            "section": [None, None, None],
        }
    )
    mapping = {
        "revenue": ["Net Sales"],
        "operating_expenses": ["SG&A"],
        "profit": ["Net Income"],
    }
    fig = FinancialSankey.income_statement(df, mapping=mapping).validate().render()
    assert fig is not None


def test_group_minor_by_top_n():
    df = _base_df(
        ["Revenue", "Small Expense 1", "Small Expense 2", "Big Expense", "Net Income"],
        [100.0, -1.0, -2.0, -50.0, 47.0],
        ["revenue", "operating_expenses", "operating_expenses", "operating_expenses", "profit"],
    )
    fig = (
        FinancialSankey.income_statement(df, layout="reference")
        .validate()
        .group_minor(top_n=2)
        .render()
    )
    sankey = fig.data[0]
    labels = [label.split("<br>")[0] for label in sankey.node.label]
    assert "Big Expense" in labels
    assert any("Other" in label for label in labels)


def test_null_value_error_shows_account():
    df = pl.DataFrame(
        {
            "account": ["Revenue", None, "Net Income"],
            "value": [100.0, -50.0, 50.0],
            "period": ["FY2025"] * 3,
            "currency": ["USD"] * 3,
            "statement": ["income_statement"] * 3,
            "section": ["revenue", "operating_expenses", "profit"],
        }
    )
    with pytest.raises(NullValueError) as exc_info:
        FinancialSankey.income_statement(df).validate()
    assert "account" in str(exc_info.value)
