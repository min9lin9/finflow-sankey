"""Tests for layout improvements."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey


def test_node_x_positions_based_on_level():
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
        .render(title="Layout Test")
    )

    sankey = fig.data[0]
    x_positions = sankey.node.x
    labels = sankey.node.label

    label_to_x = {label.split("<br>")[0]: x for label, x in zip(labels, x_positions)}

    # Income statement has variable levels depending on available sections
    assert label_to_x["Revenue"] == 0.0
    assert label_to_x["Operating Expenses"] == pytest.approx(0.5)
    assert label_to_x["Net Income"] == 1.0


def test_cash_flow_x_positions():
    df = pl.DataFrame({
        "account": ["Beginning Cash", "Operating Cash Flow", "Ending Cash"],
        "value": [100.0, 30.0, 130.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["cash_flow_statement"] * 3,
        "section": ["beginning_cash", "operating_cash_flow", "ending_cash"],
    })

    fig = (
        FinancialSankey
        .cash_flow_statement(df)
        .validate()
        .render(title="Cash Flow Layout")
    )

    sankey = fig.data[0]
    x_positions = sankey.node.x
    labels = sankey.node.label

    label_to_x = {label.split("<br>")[0]: x for label, x in zip(labels, x_positions)}

    assert label_to_x["Beginning Cash"] == 0.0
    assert label_to_x["Operating Cash Flow"] == 0.5
    assert label_to_x["Ending Cash"] == 1.0
