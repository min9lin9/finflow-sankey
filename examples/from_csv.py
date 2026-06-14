"""Example: Load income statement data from CSV and render a Sankey."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from finflow_sankey import FinancialSankey


def main() -> None:
    csv_path = Path(__file__).parent / "data" / "sample_income_statement.csv"
    df = pl.read_csv(csv_path)

    fig = (
        FinancialSankey.income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="Income Statement from CSV")
    )

    output = Path("income_statement_from_csv.html")
    fig.write_html(str(output))
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
