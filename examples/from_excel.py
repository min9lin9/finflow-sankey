"""Example: Load income statement data from Excel and render a Sankey."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from finflow_sankey import FinancialSankey


def main() -> None:
    excel_path = Path(__file__).parent / "data" / "sample_income_statement.xlsx"
    df = pl.read_excel(excel_path, sheet_name="IS")

    fig = (
        FinancialSankey.income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="Income Statement from Excel")
    )

    output = Path("income_statement_from_excel.html")
    fig.write_html(str(output))
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
