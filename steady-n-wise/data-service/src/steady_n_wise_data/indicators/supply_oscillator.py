from __future__ import annotations

import polars as pl

REQUIRED_COLUMNS = {"date", "market_cap", "foreign_net", "institution_net"}


def compute_supply_oscillator(rows: pl.DataFrame) -> pl.DataFrame:
    missing = REQUIRED_COLUMNS.difference(rows.columns)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
    if rows.is_empty():
        raise ValueError("at least one row is required")

    ordered = rows.sort("date")
    if ordered.filter(pl.col("market_cap") <= 0).height > 0:
        raise ValueError("market_cap must be positive")

    with_ratio = ordered.with_columns(
        ((pl.col("foreign_net") + pl.col("institution_net")) / pl.col("market_cap"))
        .cast(pl.Float64)
        .alias("supply_ratio")
    )
    with_macd = with_ratio.with_columns(
        pl.col("supply_ratio").ewm_mean(span=12, adjust=False).alias("ema12"),
        pl.col("supply_ratio").ewm_mean(span=26, adjust=False).alias("ema26"),
    ).with_columns((pl.col("ema12") - pl.col("ema26")).alias("macd"))

    return with_macd.with_columns(
        pl.col("macd").ewm_mean(span=9, adjust=False).alias("signal")
    ).with_columns((pl.col("macd") - pl.col("signal")).alias("oscillator"))
