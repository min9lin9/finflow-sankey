"""Tests for account mapping."""

import polars as pl

from finflow_sankey import FinancialSankey


def test_income_statement_mapping():
    df = pl.DataFrame({
        "account": ["Net Sales", "COGS", "SG&A", "Income Tax Expense", "Net Income"],
        "value": [100.0, -40.0, -30.0, -10.0, 20.0],
        "period": ["FY2025"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["income_statement"] * 5,
        "section": [None, None, None, None, None],
    })

    mapping = {
        "revenue": ["Net Sales"],
        "cost_of_revenue": ["COGS"],
        "operating_expenses": ["SG&A"],
        "tax": ["Income Tax Expense"],
        "profit": ["Net Income"],
    }

    fig = (
        FinancialSankey
        .income_statement(df, mapping=mapping)
        .validate()
        .render(title="Mapped Income Statement")
    )

    assert fig is not None


def test_yaml_mapping(tmp_path):
    import yaml

    mapping = {
        "revenue": ["Net Sales"],
        "operating_expenses": ["SG&A"],
        "profit": ["Net Income"],
    }
    yaml_path = tmp_path / "mapping.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(mapping, f)

    df = pl.DataFrame({
        "account": ["Net Sales", "SG&A", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": [None, None, None],
    })

    fig = (
        FinancialSankey
        .income_statement(df, mapping=str(yaml_path))
        .validate()
        .render(title="YAML Mapped")
    )

    assert fig is not None
