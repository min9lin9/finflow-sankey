from __future__ import annotations

from datetime import date

import polars as pl
import pytest

from steady_n_wise_data.indicators.supply_oscillator import compute_supply_oscillator


def test_supply_oscillator_matches_identity() -> None:
    frame = pl.DataFrame(
        {
            "date": [date(2026, 1, day) for day in range(2, 16)],
            "market_cap": [100_000_000_000 + day * 1_000_000 for day in range(14)],
            "foreign_net": [1_000_000 - day * 50_000 for day in range(14)],
            "institution_net": [500_000 + day * 25_000 for day in range(14)],
        }
    )

    result = compute_supply_oscillator(frame)

    assert result.height == 14
    for row in result.to_dicts():
        assert row["oscillator"] == pytest.approx(row["macd"] - row["signal"], abs=1e-12)


def test_supply_oscillator_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        compute_supply_oscillator(pl.DataFrame({"date": [date(2026, 1, 2)]}))
