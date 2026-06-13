"""Sign normalization and unit conversion."""

from __future__ import annotations

import polars as pl


UNIT_MULTIPLIERS = {
    "ones": 1.0,
    "thousands": 1_000.0,
    "millions": 1_000_000.0,
    "billions": 1_000_000_000.0,
}


class SignNormalizer:
    """Normalizes financial signs so Sankey can represent outflows as positive widths."""

    def __init__(self, expense_sign: str = "positive"):
        """
        Args:
            expense_sign: How to represent expense/outflow values internally.
                "positive" means expenses are stored as positive numbers (default for Sankey).
                "negative" keeps original sign.
        """
        self.expense_sign = expense_sign

    def normalize(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Normalize signs based on section and explicit sign override.

        Keeps original 'value' unchanged for validation, and produces 'sankey_value'
        as a positive width representation for Sankey links.
        """
        # Determine signed value considering explicit sign override
        signed_value = pl.when(pl.col("sign") == "inverse").then(-pl.col("value")).otherwise(pl.col("value"))

        cash_flow_sections = [
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_effect",
        ]

        if self.expense_sign == "positive":
            # Expenses are stored as negative values -> flip to positive for Sankey width.
            # Cash flow items already carry sign (positive=inflow, negative=outflow)
            # -> use absolute value for Sankey width.
            lf = lf.with_columns(
                pl.when(
                    pl.col("section").is_in(
                        ["expense", "cost", "cogs", "opex", "tax", "cash_outflow"]
                    )
                )
                .then(-signed_value)
                .when(pl.col("section").is_in(cash_flow_sections))
                .then(signed_value.abs())
                .otherwise(signed_value)
                .alias("sankey_value")
            )
        else:
            lf = lf.with_columns(signed_value.alias("sankey_value"))

        # Store absolute value for display metadata
        lf = lf.with_columns(pl.col("sankey_value").abs().alias("display_value"))

        return lf


class UnitNormalizer:
    """Converts units to base currency."""

    def normalize(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        # Fill null units with "ones", then map to multiplier
        lf = lf.with_columns(
            pl.col("unit")
            .fill_null("ones")
            .replace_strict(UNIT_MULTIPLIERS, default=1.0)
            .cast(pl.Float64)
            .alias("unit_multiplier")
        )
        lf = lf.with_columns(
            (pl.col("value") * pl.col("unit_multiplier")).alias("value"),
            (pl.col("sankey_value") * pl.col("unit_multiplier")).alias("sankey_value"),
            (pl.col("display_value") * pl.col("unit_multiplier")).alias("display_value"),
        )
        return lf
