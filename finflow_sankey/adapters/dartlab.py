"""Dartlab CLI adapter for FinFlow Sankey."""

from __future__ import annotations

import json
import subprocess
from typing import Literal

import polars as pl


class DartlabAdapter:
    """Adapter that wraps the system `dartlab` CLI."""

    def __init__(self, stock_code: str):
        self.stock_code = stock_code

    def _fetch(self, topic: Literal["IS", "BS", "CF"]) -> dict:
        cmd = ["dartlab", "profile", self.stock_code, "--show", topic, "--raw"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"dartlab CLI failed: {result.stderr}")
        return json.loads(result.stdout)

    def load_income_statement(self, period: str | None = None) -> pl.DataFrame:
        """Fetch income statement data from Dartlab."""
        data = self._fetch("IS")
        table = data.get("table", [])
        metrics = {row["account"]: row.get(period, row.get(next(iter(row.keys() - {"account"}), None))) for row in table}

        revenue = float(metrics.get("Revenue", 0.0))
        operating_income = float(metrics.get("Operating income", 0.0))
        net_income = float(metrics.get("Net income", 0.0))
        operating_expenses = revenue - operating_income
        tax = operating_income - net_income

        accounts = ["Revenue", "Operating Expenses", "Net Income"]
        values = [revenue, -operating_expenses, net_income]
        sections = ["revenue", "operating_expenses", "profit"]
        if tax > 0:
            accounts.append("Tax")
            values.append(-tax)
            sections.append("tax")
        elif tax < 0:
            accounts.append("Tax Benefit")
            values.append(abs(tax))
            sections.append("non_operating_items")

        return pl.DataFrame(
            {
                "account": accounts,
                "value": values,
                "period": [period or str(data.get("period", "latest"))] * len(accounts),
                "currency": [data.get("raw", {}).get("currency", "KRW")] * len(accounts),
                "statement": ["income_statement"] * len(accounts),
                "section": sections,
            }
        )

    def load_balance_sheet(self, period: str | None = None) -> pl.DataFrame:
        """Fetch balance sheet data from Dartlab."""
        data = self._fetch("BS")
        table = data.get("table", [])
        metrics = {row["account"]: row.get(period, row.get(next(iter(row.keys() - {"account"}), None))) for row in table}

        return pl.DataFrame(
            {
                "account": ["Assets", "Liabilities", "Equity"],
                "value": [
                    float(metrics.get("Assets", 0.0)),
                    float(metrics.get("Liabilities", 0.0)),
                    float(metrics.get("Equity", 0.0)),
                ],
                "period": [period or str(data.get("period", "latest"))] * 3,
                "currency": [data.get("raw", {}).get("currency", "KRW")] * 3,
                "statement": ["balance_sheet"] * 3,
                "section": ["asset", "liability", "equity"],
            }
        )
