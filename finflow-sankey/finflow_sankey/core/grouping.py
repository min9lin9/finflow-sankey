from __future__ import annotations

import polars as pl


def group_by_threshold(df: pl.DataFrame, threshold: float, label: str) -> pl.DataFrame:
    threshold = max(threshold, 0.0)
    grouped_df = df.with_columns(
        pl.when(pl.col("sankey_value") < threshold)
        .then(pl.lit(label))
        .otherwise(pl.col("account"))
        .alias("account_group")
    )
    return finalize_group_label(_aggregate_grouped(grouped_df), label)


def group_by_top_n(df: pl.DataFrame, top_n: int, label: str) -> pl.DataFrame:
    if top_n <= 0:
        raise ValueError("top_n must be a positive integer.")

    top_accounts = df.sort("sankey_value", descending=True).head(top_n)["account"].to_list()
    grouped_df = df.with_columns(
        pl.when(pl.col("account").is_in(top_accounts))
        .then(pl.col("account"))
        .otherwise(pl.lit(label))
        .alias("account_group")
    )
    return finalize_group_label(_aggregate_grouped(grouped_df), label)


def finalize_group_label(grouped: pl.DataFrame, label: str) -> pl.DataFrame:
    grouped = grouped.with_columns(
        pl.when(pl.col("account_group") == label)
        .then(True)
        .otherwise(False)
        .alias("is_grouped"),
    )
    return grouped.with_columns(
        pl.when(pl.col("is_grouped"))
        .then(
            pl.lit(f"{label} (")
            + pl.col("original_accounts").list.len().cast(pl.Utf8)
            + pl.lit(" accounts)")
        )
        .otherwise(pl.col("account_group"))
        .alias("account")
    )


def _aggregate_grouped(df: pl.DataFrame) -> pl.DataFrame:
    return df.group_by(["account_group", "section"]).agg(
        pl.col("value").sum().alias("value"),
        pl.col("sankey_value").sum().alias("sankey_value"),
        pl.col("display_value").sum().alias("display_value"),
        pl.col("period").first().alias("period"),
        pl.col("currency").first().alias("currency"),
        pl.col("statement").first().alias("statement"),
        pl.col("account").alias("original_accounts"),
    )
