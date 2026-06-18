"""Tests for HTML export helper."""

import os
from pathlib import Path

import polars as pl

from finflow_sankey import FinancialSankey


def test_export_html(tmp_path):
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    output_path = tmp_path / "output.html"
    result = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .export_html(output_path, title="Export Test")
    )

    assert result == str(output_path)
    assert Path(output_path).exists()
    assert os.path.getsize(output_path) > 0


def test_export_html_with_theme(tmp_path):
    df = pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Net Income"],
        "value": [100.0, -40.0, 60.0],
        "period": ["FY2025"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["income_statement"] * 3,
        "section": ["revenue", "expense", "profit"],
    })

    output_path = tmp_path / "output_theme.html"
    result = (
        FinancialSankey
        .income_statement(df)
        .validate()
        .export_html(output_path, title="Export Theme", theme="minimal")
    )

    assert result == str(output_path)
    assert Path(output_path).exists()
