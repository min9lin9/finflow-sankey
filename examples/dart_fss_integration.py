"""Example: Fetch detailed financial statements from DART via dart-fss.

This example uses the `dart-fss` library (https://github.com/josw123/dart-fss)
to extract Samsung Electronics' income statement and visualize it.

You need a DART OpenAPI key. Get one at:
https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do

Set it before running:

    export DART_API_KEY="your-api-key"
"""

from __future__ import annotations

import os

import dart_fss as dart
import polars as pl

from finflow_sankey import FinancialSankey


def fetch_income_statement(corp_code: str = "00126380") -> pl.DataFrame:
    """Fetch the latest consolidated income statement from DART."""
    api_key = os.environ.get("DART_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the DART_API_KEY environment variable.")

    dart.set_api_key(api_key=api_key)
    corp_list = dart.get_corp_list()
    corp = corp_list.find_by_corp_code(corp_code)

    # Extract financial statements for the latest 2 years
    fs = corp.extract_fs(bgn_de="20230101")

    # Consolidated income statement
    cis = fs["cis"]

    # dart-fss returns a MultiIndex DataFrame. Adapt columns for the latest period.
    # This example assumes the last column is the most recent period.
    latest_col = cis.columns[-1]
    df = cis[[latest_col]].reset_index()
    df.columns = ["account", "value"]
    df["value"] = df["value"].astype(float)

    # Map common DART account names to FinFlow sections
    section_map = {
        "매출액": "revenue",
        "영업이익": "operating_income",
        "당기순이익": "profit",
    }

    df["section"] = df["account"].map(section_map)
    df = df.dropna(subset=["section"])

    # Derive implied operating expenses for a complete flow
    revenue = float(df.loc[df["section"] == "revenue", "value"].iloc[0])
    operating_income = float(df.loc[df["section"] == "operating_income", "value"].iloc[0])
    net_income = float(df.loc[df["section"] == "profit", "value"].iloc[0])

    rows = [
        {"account": "Revenue", "value": revenue, "section": "revenue"},
        {"account": "Operating Expenses", "value": -(revenue - operating_income), "section": "operating_expenses"},
        {"account": "Net Income", "value": net_income, "section": "profit"},
    ]

    period = str(latest_col)
    result = pl.DataFrame(rows)
    result = result.with_columns(
        pl.lit(period).alias("period"),
        pl.lit("KRW").alias("currency"),
        pl.lit("income_statement").alias("statement"),
    )
    return result


def main() -> None:
    df = fetch_income_statement()
    print(df)

    fig = (
        FinancialSankey.income_statement(df, period=df["period"][0], currency="KRW")
        .validate()
        .render(title="Samsung Electronics Income Statement (DART)")
    )
    fig.write_html("005930_dart_fss_income_statement.html")
    print("Saved: 005930_dart_fss_income_statement.html")


if __name__ == "__main__":
    main()
