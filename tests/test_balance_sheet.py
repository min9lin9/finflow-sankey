"""Tests for balance sheet reconciliation Sankey."""

import polars as pl
import pytest

from finflow_sankey import FinancialSankey
from finflow_sankey.core.exceptions import ReconciliationError


def test_balance_sheet_reconciliation():
    df = pl.DataFrame({
        "account": [
            "Current Assets",
            "Non-current Assets",
            "Current Liabilities",
            "Non-current Liabilities",
            "Equity",
        ],
        "value": [60.0, 40.0, 30.0, 20.0, 50.0],
        "period": ["2025-12-31"] * 5,
        "currency": ["USD"] * 5,
        "statement": ["balance_sheet"] * 5,
        "section": [
            "current_asset",
            "non_current_asset",
            "current_liability",
            "non_current_liability",
            "equity",
        ],
    })

    fig = (
        FinancialSankey
        .balance_sheet_reconciliation(df, as_of="2025-12-31", currency="USD")
        .validate()
        .render(title="Balance Sheet")
    )

    assert fig is not None
    assert "Reconciliation View" in fig.layout.title.text

    sankey = fig.data[0]
    labels = sankey.node.label
    assert "Total Assets" in labels
    assert "Total Liabilities and Equity" in labels


def test_balance_sheet_reconciliation_error():
    df = pl.DataFrame({
        "account": [
            "Current Assets",
            "Current Liabilities",
            "Equity",
        ],
        "value": [60.0, -30.0, -20.0],  # assets 60 != liabilities+equity 50
        "period": ["2025-12-31"] * 3,
        "currency": ["USD"] * 3,
        "statement": ["balance_sheet"] * 3,
        "section": ["current_asset", "current_liability", "equity"],
    })

    with pytest.raises(ReconciliationError):
        FinancialSankey.balance_sheet_reconciliation(df).validate()
