"""Tests for data adapters."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from finflow_sankey.adapters import (
    DartlabAdapter,
    load_balance_sheet_csv,
    load_cash_flow_csv,
    load_income_statement_csv,
    load_income_statement_excel,
)


def test_load_income_statement_csv(tmp_path: Path):
    csv_path = tmp_path / "is.csv"
    csv_path.write_text(
        "account,value,section\n"
        "Revenue,100.0,revenue\n"
        "Operating Expenses,-50.0,operating_expenses\n"
        "Net Income,50.0,profit\n"
    )
    df = load_income_statement_csv(csv_path, period="FY2025", currency="USD")
    assert set(df.columns) == {"account", "value", "section", "period", "currency", "statement"}
    assert df["statement"][0] == "income_statement"


def test_load_cash_flow_csv(tmp_path: Path):
    csv_path = tmp_path / "cf.csv"
    csv_path.write_text(
        "account,value,section\n"
        "Beginning Cash,100.0,beginning_cash\n"
        "Operating Cash Flow,50.0,operating_cash_flow\n"
        "Ending Cash,150.0,ending_cash\n"
    )
    df = load_cash_flow_csv(csv_path, period="FY2025", currency="USD")
    assert df["statement"][0] == "cash_flow_statement"


def test_load_balance_sheet_csv(tmp_path: Path):
    csv_path = tmp_path / "bs.csv"
    csv_path.write_text(
        "account,value,section\n"
        "Assets,1000.0,asset\n"
        "Liabilities,400.0,liability\n"
        "Equity,600.0,equity\n"
    )
    df = load_balance_sheet_csv(csv_path, period="2025-12-31", currency="USD")
    assert df["statement"][0] == "balance_sheet"


def test_csv_section_mapping(tmp_path: Path):
    csv_path = tmp_path / "is.csv"
    csv_path.write_text(
        "account,value,section\n"
        "Sales,100.0,Sales\n"
        "Costs,-50.0,Costs\n"
        "Net Income,50.0,Net Income\n"
    )
    df = load_income_statement_csv(
        csv_path,
        period="FY2025",
        currency="USD",
        section_mapping={"Sales": "revenue", "Costs": "operating_expenses", "Net Income": "profit"},
    )
    assert set(df["section"].to_list()) == {"revenue", "operating_expenses", "profit"}


def test_load_income_statement_excel(tmp_path: Path):
    df_in = pl.DataFrame(
        {
            "account": ["Revenue", "Operating Expenses", "Net Income"],
            "value": [100.0, -50.0, 50.0],
            "section": ["revenue", "operating_expenses", "profit"],
        }
    )
    excel_path = tmp_path / "is.xlsx"
    df_in.write_excel(excel_path, worksheet="IS")

    df = load_income_statement_excel(excel_path, sheet_name="IS", period="FY2025", currency="USD")
    assert df["statement"][0] == "income_statement"
    assert len(df) == 3


def test_dartlab_adapter_import():
    assert DartlabAdapter is not None
