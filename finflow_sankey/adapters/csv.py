"""CSV adapter helpers for FinFlow Sankey."""

from __future__ import annotations

from pathlib import Path

import polars as pl


def _load_csv(
    path: str | Path,
    statement_type: str,
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load a CSV file and prepare it for FinFlow Sankey."""
    df = pl.read_csv(path)
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


def load_income_statement_csv(
    path: str | Path,
    *,
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load an income statement CSV file."""
    return _load_csv(path, "income_statement", period, currency, section_mapping)


def load_cash_flow_csv(
    path: str | Path,
    *,
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load a cash flow statement CSV file."""
    return _load_csv(path, "cash_flow_statement", period, currency, section_mapping)


def load_balance_sheet_csv(
    path: str | Path,
    *,
    period: str,
    currency: str,
    section_mapping: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Load a balance sheet CSV file."""
    return _load_csv(path, "balance_sheet", period, currency, section_mapping)
