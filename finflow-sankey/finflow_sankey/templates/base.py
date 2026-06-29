"""Base template for financial statement Sankey."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import polars as pl

from finflow_sankey.core.graph import FinancialGraph


class StatementTemplate(ABC):
    """Abstract base class for financial statement templates."""

    statement_type: str = ""

    @abstractmethod
    def build(self, df: pl.DataFrame, **kwargs: Any) -> FinancialGraph:
        """Build a FinancialGraph from normalized data."""

    @abstractmethod
    def required_roles(self) -> set[str]:
        """Return required roles for this statement type."""
