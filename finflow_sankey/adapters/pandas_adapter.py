"""Optional pandas adapter for FinFlow Sankey."""

from __future__ import annotations

import polars as pl


def to_polars(df):
    """Convert a pandas DataFrame to a Polars DataFrame.

    Raises ImportError if pandas is not installed.
    Raises TypeError if input is not a pandas DataFrame.
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "pandas is required for this feature. "
            "Install with: pip install finflow-sankey[pandas]"
        ) from e

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

    return pl.from_pandas(df)
