"""Internal graph representation for Sankey."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SankeyNode:
    """Represents a single Sankey node."""

    node_id: str
    label: str
    role: str
    level: int
    amount: float
    display_amount: float
    metadata: dict = field(default_factory=dict)
    x: float | None = None
    y: float | None = None


@dataclass
class SankeyLink:
    """Represents a single Sankey link."""

    source: str
    target: str
    source_idx: int
    target_idx: int
    amount: float
    display_amount: float
    flow_type: str = "flow"
    metadata: dict = field(default_factory=dict)


@dataclass
class FinancialGraph:
    """Container for Sankey nodes and links."""

    nodes: list[SankeyNode]
    links: list[SankeyLink]
    period: str | None = None
    currency: str | None = None
    statement_type: str | None = None
    metadata: dict = field(default_factory=dict)

    def get_node_index(self, node_id: str) -> int:
        for i, node in enumerate(self.nodes):
            if node.node_id == node_id:
                return i
        raise KeyError(f"Node '{node_id}' not found.")

    def get_role_amount(self, role: str) -> float:
        return sum((node.amount for node in self.nodes if node.role == role), 0.0)
