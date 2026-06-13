"""Example: Use Dartlab CLI to fetch real DART data and visualize with FinFlow Sankey.

This script uses subprocess to call the system `dartlab` CLI (Python 3.12+)
and processes the returned JSON with Polars only (no pandas).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import polars as pl

from finflow_sankey import FinancialSankey


def fetch_dartlab_profile(stock_code: str, topic: str) -> dict:
    """Call dartlab CLI profile --show <topic> --raw and return parsed JSON."""
    cmd = ["dartlab", "profile", stock_code, "--show", topic, "--raw"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print(f"dartlab CLI failed: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"dartlab profile {stock_code} {topic} failed")

    if not result.stdout.strip():
        raise RuntimeError(f"No data returned for topic '{topic}'")

    return json.loads(result.stdout)


def build_income_statement_from_dartlab(data: dict, period: str) -> pl.DataFrame:
    """Convert Dartlab IS JSON to FinFlow Sankey schema."""
    table = data.get("table", [])

    # Find key metrics
    metrics = {row["account"]: row.get(period, 0.0) for row in table}

    revenue = metrics.get("Revenue", 0.0)
    operating_income = metrics.get("Operating income", 0.0)
    net_income = metrics.get("Net income", 0.0)

    # Derive implied operating expenses and tax for visualization
    operating_expenses = revenue - operating_income
    tax = operating_income - net_income

    return pl.DataFrame({
        "account": ["Revenue", "Operating Expenses", "Tax", "Net Income"],
        "value": [revenue, -operating_expenses, -tax, net_income],
        "period": [period] * 4,
        "currency": ["KRW tn"] * 4,
        "statement": ["income_statement"] * 4,
        "section": ["revenue", "operating_expenses", "tax", "profit"],
    })


def build_balance_sheet_from_dartlab(data: dict, period: str) -> pl.DataFrame:
    """Convert Dartlab BS JSON to FinFlow Sankey schema."""
    table = data.get("table", [])
    metrics = {row["account"]: row.get(period, 0.0) for row in table}

    return pl.DataFrame({
        "account": ["Assets", "Liabilities", "Equity"],
        "value": [
            metrics.get("Assets", 0.0),
            metrics.get("Liabilities", 0.0),
            metrics.get("Equity", 0.0),
        ],
        "period": [period] * 3,
        "currency": ["KRW tn"] * 3,
        "statement": ["balance_sheet"] * 3,
        "section": ["asset", "liability", "equity"],
    })


def main():
    stock_code = "005930"  # Samsung Electronics
    period = "2024"

    print(f"Fetching DART data for {stock_code}...")

    # Income statement
    is_data = fetch_dartlab_profile(stock_code, "IS")
    is_df = build_income_statement_from_dartlab(is_data, period)

    print("Income statement data:")
    print(is_df)

    is_fig = (
        FinancialSankey
        .income_statement(is_df, period=period, currency="KRW tn")
        .validate()
        .render(title=f"{stock_code} Income Statement {period}")
    )
    is_fig.write_html(f"{stock_code}_income_statement.html")
    print(f"Saved: {stock_code}_income_statement.html")

    # Balance sheet
    bs_data = fetch_dartlab_profile(stock_code, "BS")
    bs_df = build_balance_sheet_from_dartlab(bs_data, period)

    print("Balance sheet data:")
    print(bs_df)

    bs_fig = (
        FinancialSankey
        .balance_sheet_reconciliation(bs_df, as_of=period, currency="KRW tn")
        .validate()
        .render(title=f"{stock_code} Balance Sheet {period}")
    )
    bs_fig.write_html(f"{stock_code}_balance_sheet.html")
    print(f"Saved: {stock_code}_balance_sheet.html")


if __name__ == "__main__":
    main()
