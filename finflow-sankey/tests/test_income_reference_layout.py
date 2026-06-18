"""Tests for the opt-in reference income statement layout."""

from __future__ import annotations

import polars as pl

from finflow_sankey import FinancialSankey


def reference_income_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "account": [
                "Product Sales",
                "Service Sales",
                "Cost of Sales",
                "Payroll",
                "Rent",
                "Transport",
                "Net Income",
            ],
            "value": [156.0, 73.0, -163.0, -18.0, -9.0, -5.0, 34.0],
            "period": ["FY2025"] * 7,
            "currency": ["KRW"] * 7,
            "statement": ["income_statement"] * 7,
            "section": [
                "revenue",
                "revenue",
                "cost_of_revenue",
                "operating_expenses",
                "operating_expenses",
                "operating_expenses",
                "profit",
            ],
        }
    )


def test_reference_layout_uses_fixed_arrangement():
    fig = (
        FinancialSankey.income_statement(reference_income_df(), layout="reference")
        .validate()
        .render(title="Reference Style")
    )
    sankey = fig.data[0]
    assert sankey.arrangement == "fixed"


def test_reference_layout_creates_detail_nodes():
    fig = (
        FinancialSankey.income_statement(reference_income_df(), layout="reference")
        .validate()
        .render(title="Reference Style")
    )
    sankey = fig.data[0]
    labels = [label.split("<br>")[0] for label in sankey.node.label]

    assert "Product Sales" in labels
    assert "Service Sales" in labels
    assert "Total Revenue" in labels
    assert "Payroll" in labels
    assert "Rent" in labels
    assert "Transport" in labels
    assert "Gross Profit" in labels
    assert "Operating Income" in labels
    assert "Net Income" in labels


def test_reference_layout_positions():
    fig = (
        FinancialSankey.income_statement(reference_income_df(), layout="reference")
        .validate()
        .render(title="Reference Style")
    )
    sankey = fig.data[0]
    labels = [label.split("<br>")[0] for label in sankey.node.label]
    label_to_x = dict(zip(labels, sankey.node.x))
    label_to_y = dict(zip(labels, sankey.node.y))

    assert label_to_x["Product Sales"] == 0.0
    assert label_to_x["Total Revenue"] == 0.25
    assert label_to_x["Gross Profit"] == 0.5
    assert label_to_x["Net Income"] == 1.0

    assert label_to_y["Gross Profit"] < 0.5
    assert label_to_y["Cost of Sales"] > 0.5


def test_reference_layout_is_palette_based():
    fig = (
        FinancialSankey.income_statement(reference_income_df(), layout="reference")
        .validate()
        .render(
            title="Reference Style With Custom Palette",
            palette={"gross_profit": "#FF00FF"},
        )
    )
    sankey = fig.data[0]
    labels = [label.split("<br>")[0] for label in sankey.node.label]
    label_to_color = dict(zip(labels, sankey.node.color))

    assert label_to_color["Gross Profit"] == "#FF00FF"


def test_standard_layout_not_reference():
    fig = (
        FinancialSankey.income_statement(reference_income_df())
        .validate()
        .render(title="Standard Style")
    )
    sankey = fig.data[0]
    assert sankey.arrangement == "snap"
    labels = [label.split("<br>")[0] for label in sankey.node.label]
    assert "Product Sales" not in labels


def test_reference_layout_works_with_dark_theme():
    fig = (
        FinancialSankey.income_statement(reference_income_df(), layout="reference")
        .validate()
        .render(title="Reference Dark", theme="dark")
    )
    sankey = fig.data[0]
    assert sankey.arrangement == "fixed"
