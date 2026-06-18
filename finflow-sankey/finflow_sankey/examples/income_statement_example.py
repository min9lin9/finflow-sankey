"""Example: Income statement Sankey with custom palette."""

from __future__ import annotations

import polars as pl

from finflow_sankey import FinancialSankey


def main():
    # Sample income statement data
    df = pl.DataFrame({
        "account": [
            "Net Sales",
            "Cost of Revenue",
            "SG&A",
            "R&D",
            "Income Tax Expense",
            "Net Income",
        ],
        "value": [100_000_000.0, -40_000_000.0, -20_000_000.0, -10_000_000.0, -10_000_000.0, 20_000_000.0],
        "period": ["FY2025"] * 6,
        "currency": ["USD"] * 6,
        "statement": ["income_statement"] * 6,
        "section": [
            "revenue",
            "cost_of_revenue",
            "operating_expenses",
            "operating_expenses",
            "tax",
            "profit",
        ],
    })

    # Default theme
    fig_default = (
        FinancialSankey
        .income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="FY2025 Income Statement (Default)")
    )
    fig_default.write_html("income_statement_default.html")
    print("Saved: income_statement_default.html")

    # Colorblind-safe theme
    fig_cb = (
        FinancialSankey
        .income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="FY2025 Income Statement (Colorblind Safe)", theme="colorblind_safe")
    )
    fig_cb.write_html("income_statement_colorblind.html")
    print("Saved: income_statement_colorblind.html")

    # Custom palette override
    fig_custom = (
        FinancialSankey
        .income_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(
            title="FY2025 Income Statement (Custom)",
            palette={"revenue": "#0055FF", "profit": "#00AA55", "operating_expenses": "#CC0000"},
        )
    )
    fig_custom.write_html("income_statement_custom.html")
    print("Saved: income_statement_custom.html")


if __name__ == "__main__":
    main()
