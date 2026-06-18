from __future__ import annotations

from typing import Any

import polars as pl

from finflow_sankey.core.graph import FinancialGraph
from finflow_sankey.templates._income_reference import build_reference_income_statement
from finflow_sankey.templates._income_standard import build_standard_income_statement
from finflow_sankey.templates.base import StatementTemplate


class IncomeStatementTemplate(StatementTemplate):
    statement_type = "income_statement"

    def __init__(self, layout: str | None = None):
        self.layout = layout

    def required_roles(self) -> set[str]:
        return {"revenue", "profit"}

    def build(self, df: pl.DataFrame, **kwargs: Any) -> FinancialGraph:
        layout = kwargs.get("layout") or self.layout
        if layout == "reference":
            return build_reference_income_statement(df)
        return build_standard_income_statement(df)
