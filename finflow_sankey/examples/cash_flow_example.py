"""Example: Cash flow statement Sankey."""

from __future__ import annotations

import polars as pl

from finflow_sankey import FinancialSankey


def main():
    df = pl.DataFrame({
        "account": [
            "Beginning Cash",
            "Cash from Operations",
            "CapEx",
            "Dividends Paid",
            "FX Effect",
            "Ending Cash",
        ],
        "value": [50_000_000.0, 25_000_000.0, -10_000_000.0, -5_000_000.0, 2_000_000.0, 62_000_000.0],
        "period": ["FY2025"] * 6,
        "currency": ["USD"] * 6,
        "statement": ["cash_flow_statement"] * 6,
        "section": [
            "beginning_cash",
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_effect",
            "ending_cash",
        ],
    })

    fig = (
        FinancialSankey
        .cash_flow_statement(df, period="FY2025", currency="USD")
        .validate()
        .render(title="FY2025 Cash Flow Bridge")
    )

    fig.write_html("cash_flow_bridge.html")
    print("Saved: cash_flow_bridge.html")


if __name__ == "__main__":
    main()
