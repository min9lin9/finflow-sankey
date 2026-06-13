"""FinFlow Sankey: Polars-first financial statement Sankey visualization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from finflow_sankey.core.mapper import AccountMapper
from finflow_sankey.core.palette import ColorPalette
from finflow_sankey.core.pipeline import SankeyPipeline
from finflow_sankey.templates.income_statement import IncomeStatementTemplate


SankeyData = pl.DataFrame | pl.LazyFrame
SankeyMapping = AccountMapper | dict[str, Any] | str | Path | None
SankeyPalette = ColorPalette | dict[str, Any] | str | Path | None


class FinancialSankey:
    """Main entry point for FinFlow Sankey."""

    @classmethod
    def income_statement(
        cls,
        data: SankeyData,
        *,
        period: str | None = None,
        currency: str | None = None,
        mapping: SankeyMapping = None,
    ) -> SankeyPipeline:
        """Create an income statement Sankey pipeline."""
        template = IncomeStatementTemplate()
        return SankeyPipeline(
            data=data,
            template=template,
            period=period,
            currency=currency,
            mapping=mapping,
        )

    @classmethod
    def cash_flow_statement(
        cls,
        data: SankeyData,
        *,
        period: str | None = None,
        currency: str | None = None,
        mapping: SankeyMapping = None,
    ) -> SankeyPipeline:
        """Create a cash flow statement Sankey pipeline."""
        from finflow_sankey.templates.cash_flow import CashFlowStatementTemplate

        template = CashFlowStatementTemplate()
        return SankeyPipeline(
            data=data,
            template=template,
            period=period,
            currency=currency,
            mapping=mapping,
        )

    @classmethod
    def balance_sheet_reconciliation(
        cls,
        data: SankeyData,
        *,
        as_of: str | None = None,
        currency: str | None = None,
        mapping: SankeyMapping = None,
    ) -> SankeyPipeline:
        """Create a balance sheet reconciliation Sankey pipeline."""
        from finflow_sankey.templates.balance_sheet import BalanceSheetReconciliationTemplate

        template = BalanceSheetReconciliationTemplate()
        return SankeyPipeline(
            data=data,
            template=template,
            period=as_of,
            currency=currency,
            mapping=mapping,
        )

    @classmethod
    def multi_period_compare(
        cls,
        data: SankeyData,
        *,
        currency: str | None = None,
        mapping: SankeyMapping = None,
    ) -> SankeyPipeline:
        """Create a multi-period comparison Sankey pipeline."""
        from finflow_sankey.templates.multi_period import MultiPeriodComparisonTemplate

        template = MultiPeriodComparisonTemplate()
        return SankeyPipeline(
            data=data,
            template=template,
            period=None,
            currency=currency,
            mapping=mapping,
        )


__all__ = ["FinancialSankey", "SankeyPipeline"]
