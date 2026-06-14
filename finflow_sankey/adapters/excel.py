"""Excel adapter helpers for FinFlow Sankey."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def _load_excel(
    path: str | Path,
    sheet_name: str,
    statement_type: str,
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load an Excel sheet and prepare it for FinFlow Sankey."""
    df = pl.read_excel(path, sheet_name=sheet_name)
    df = df.with_columns(
        pl.lit(statement_type).alias("statement"),
        pl.lit(period).alias("period"),
        pl.lit(currency).alias("currency"),
    )
    if section_mapping:
        df = df.with_columns(
            pl.col("section").replace_strict(section_mapping, default=pl.col("section"))
        )
    return df


def load_income_statement_excel(
    path: str | Path,
    *,
    sheet_name: str = "IS",
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load an income statement Excel sheet."""
    return _load_excel(path, sheet_name, "income_statement", period, currency, section_mapping)


def load_cash_flow_excel(
    path: str | Path,
    *,
    sheet_name: str = "CF",
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load a cash flow statement Excel sheet."""
    return _load_excel(path, sheet_name, "cash_flow_statement", period, currency, section_mapping)


def load_balance_sheet_excel(
    path: str | Path,
    *,
    sheet_name: str = "BS",
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load a balance sheet Excel sheet."""
    return _load_excel(path, sheet_name, "balance_sheet", period, currency, section_mapping)
