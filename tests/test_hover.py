"""Tests for hover metadata."""

import polars as pl

from finflow_sankey import FinancialSankey


def test_node_hover_contains_original_accounts():
    df = pl.DataFrame({
        "account": ["Net Sales", "Cost of Revenue", "SG&A", "R&D", "Net Income"],
        "value": [100.0, -40.0, -20.0, -10.0, 30.0],
        "period": ["FY2025"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["income_statement"] * 5,
        "section": ["revenue", "cost_of_revenue", "operating_expenses", "operating_expenses", "profit"],
    })

    fig = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .render(title="Hover Test")
    )

    sankey = fig.data[0]
    hover_texts = sankey.node.customdata

    # Find Operating Expenses node hover text
    labels = sankey.node.label
    for i, label in enumerate(labels):
        if label == "Operating Expenses":
            hover = hover_texts[i]
            assert "SG&A" in hover
            assert "R&D" in hover
            assert "Original accounts" in hover


def test_cash_flow_hover_contains_accounts():
    df = pl.DataFrame({
        "account": [
            "Beginning Cash",
            "Cash from Operations",
            "CapEx",
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
        .render(title="Cash Flow Hover Test")
    )

    sankey = fig.data[0]
    hover_texts = sankey.node.customdata
    assert any("Cash from Operations" in hover for hover in hover_texts)
