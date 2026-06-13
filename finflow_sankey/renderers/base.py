"""Base renderer for financial Sankey graphs."""

from __future__ import annotations

from abc import ABC, abstractmethod

from finflow_sankey.core.graph import FinancialGraph
from finflow_sankey.core.palette import ColorPalette


class Renderer(ABC):
    """Abstract base class for Sankey renderers."""

    @abstractmethod
    def render(self, graph: FinancialGraph, palette: ColorPalette, title: str | None = None):
        """Render a FinancialGraph."""
        pass
