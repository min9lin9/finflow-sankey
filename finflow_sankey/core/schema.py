"""Input schema validation and constants."""

from __future__ import annotations

import polars as pl

from .exceptions import MissingColumnError, SchemaError


REQUIRED_COLUMNS = ["account", "value", "period", "currency", "statement"]

OPTIONAL_COLUMNS = [
    "account_id",
    "parent",
    "section",
    "concept",
    "unit",
    "sign",
]

VALID_UNITS = {"ones", "thousands", "millions", "billions"}
VALID_SIGNS = {"normal", "inverse"}
VALID_SECTIONS = {
    "revenue",
    "expense",
    "profit",
    "asset",
    "liability",
    "equity",
    "cashflow",
}


class InputSchema:
    """Validates and normalizes input financial data schema."""

    def __init__(self, data: pl.DataFrame | pl.LazyFrame):
        self._lf = data.lazy() if isinstance(data, pl.DataFrame) else data

    def validate(self) -> "InputSchema":
        """Validate required columns exist."""
        schema = self._lf.collect_schema()
        columns = set(schema.names())

        for col in REQUIRED_COLUMNS:
            if col not in columns:
                raise MissingColumnError(col)

        # Validate value is numeric
        value_dtype = schema["value"]
        if value_dtype not in (pl.Float64, pl.Float32, pl.Int64, pl.Int32):
            raise SchemaError("Column 'value' must be numeric.")

        return self

    def normalize(self) -> pl.LazyFrame:
        """Return a normalized LazyFrame with optional columns added if missing."""
        lf = self._lf
        columns = set(lf.collect_schema().names())

        for col in OPTIONAL_COLUMNS:
            if col not in columns:
                lf = lf.with_columns(pl.lit(None).alias(col))

        # Normalize account name to string
        lf = lf.with_columns(pl.col("account").cast(pl.Utf8))

        # Ensure value is float64
        lf = lf.with_columns(pl.col("value").cast(pl.Float64))

        # Add metadata columns
        if "row_id" not in columns:
            lf = lf.with_row_index("row_id")

        return lf

    @property
    def lazy_frame(self) -> pl.LazyFrame:
        return self._lf
