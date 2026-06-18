"""Performance benchmarks for FinFlow Sankey rendering."""

from __future__ import annotations

import polars as pl
import pytest

from finflow_sankey import FinancialSankey


def _make_income_df(n_expense_accounts: int) -> pl.DataFrame:
    revenue = 1_000_000_000.0
    expense_per_account = revenue / (n_expense_accounts + 2)
    accounts = ["Revenue"]
    values = [revenue]
    sections = ["revenue"]
    for i in range(n_expense_accounts):
        accounts.append(f"Expense {i + 1}")
        values.append(-expense_per_account)
        sections.append("operating_expenses")
    profit = revenue - (n_expense_accounts * expense_per_account)
    accounts.append("Net Income")
    values.append(profit)
    sections.append("profit")
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


@pytest.mark.benchmark
@pytest.mark.parametrize("n_accounts", [10, 50, 100])
def test_standard_render_performance(benchmark, n_accounts: int):
    df = _make_income_df(n_accounts)
    pipeline = FinancialSankey.income_statement(df).validate()

    def render():
        return pipeline.render()

    result = benchmark(render)
    assert result is not None


@pytest.mark.benchmark
@pytest.mark.parametrize("n_accounts", [10, 50, 100])
def test_reference_render_performance(benchmark, n_accounts: int):
    df = _make_income_df(n_accounts)
    pipeline = FinancialSankey.income_statement(df, layout="reference").validate()

    def render():
        return pipeline.render()

    result = benchmark(render)
    assert result is not None
