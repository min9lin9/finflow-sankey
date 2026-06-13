"""FinFlow Sankey: Polars-first financial statement Sankey visualization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from finflow_sankey.core.mapper import AccountMapper
from finflow_sankey.core.pipeline import SankeyPipeline
from finflow_sankey.templates.income_statement import IncomeStatementTemplate


class FinancialSankey:
    """Main entry point for FinFlow Sankey."""

    @classmethod
    def income_statement(
        cls,
        data: pl.DataFrame | pl.LazyFrame,
        *,
        period: str | None = None,
        currency: str | None = None,
        mapping: AccountMapper | dict[str, Any] | str | Path | None = None,
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
        data: pl.DataFrame | pl.LazyFrame,
        *,
        period: str | None = None,
        currency: str | None = None,
        mapping: AccountMapper | dict[str, Any] | str | Path | None = None,
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
        data: pl.DataFrame | pl.LazyFrame,
        *,
        as_of: str | None = None,
        currency: str | None = None,
        mapping: AccountMapper | dict[str, Any] | str | Path | None = None,
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
        data: pl.DataFrame | pl.LazyFrame,
        *,
        currency: str | None = None,
        mapping: AccountMapper | dict[str, Any] | str | Path | None = None,
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
