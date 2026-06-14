"""Multi-period comparison Sankey template."""

from __future__ import annotations

from typing import Any

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates.base import StatementTemplate


class MultiPeriodComparisonTemplate(StatementTemplate):
    """Builds a Sankey comparing two periods side-by-side.

    Nodes are placed with previous period on the left and current period on the right.
    Links connect matching sections and are colored by growth/decline.
    """

    statement_type = "multi_period_comparison"

    def required_roles(self) -> set[str]:
        return set()

    def build(self, df: pl.DataFrame, **kwargs: Any) -> FinancialGraph:
        """Build multi-period comparison Sankey."""
        periods = sorted(df["period"].unique().to_list())
        if len(periods) != 2:
            raise ValueError("Multi-period comparison requires exactly 2 periods.")

        prev_period, curr_period = periods
        currency = df["currency"][0] if len(df) > 0 else None

        nodes: list[SankeyNode] = []
        links: list[SankeyLink] = []
        node_index: dict[str, int] = {}

        # Aggregate by (period, section)
        sections = df["section"].unique().to_list()

        for section in sections:
            prev_df = df.filter((df["section"] == section) & (df["period"] == prev_period))
            curr_df = df.filter((df["section"] == section) & (df["period"] == curr_period))

            prev_amount = prev_df["sankey_value"].sum() if len(prev_df) > 0 else 0.0
            curr_amount = curr_df["sankey_value"].sum() if len(curr_df) > 0 else 0.0

            prev_accounts = prev_df["account"].to_list() if len(prev_df) > 0 else []
            curr_accounts = curr_df["account"].to_list() if len(curr_df) > 0 else []

            if prev_amount == 0.0 and curr_amount == 0.0:
                continue

            prev_node_id = f"{section}_{prev_period}"
            curr_node_id = f"{section}_{curr_period}"

            # Determine role by section semantics
            role = self._section_role(section)

            # Previous period node
            nodes.append(
                SankeyNode(
                    node_id=prev_node_id,
                    label=f"{section.replace('_', ' ').title()} ({prev_period})",
                    role=role,
                    level=0,
                    x=0.0,
                    amount=prev_amount,
                    display_amount=prev_amount,
                    metadata={
                        "section": section,
                        "period": prev_period,
                        "original_accounts": prev_accounts,
                    },
                )
            )
            node_index[prev_node_id] = len(nodes) - 1

            # Current period node
            nodes.append(
                SankeyNode(
                    node_id=curr_node_id,
                    label=f"{section.replace('_', ' ').title()} ({curr_period})",
                    role=role,
                    level=1,
                    x=1.0,
                    amount=curr_amount,
                    display_amount=curr_amount,
                    metadata={
                        "section": section,
                        "period": curr_period,
                        "original_accounts": curr_accounts,
                    },
                )
            )
            node_index[curr_node_id] = len(nodes) - 1

            change_amount = abs(curr_amount - prev_amount)
            if change_amount > 0:
                flow_type = "growth" if curr_amount >= prev_amount else "decline"
                links.append(
                    SankeyLink(
                        source=prev_node_id,
                        target=curr_node_id,
                        source_idx=node_index[prev_node_id],
                        target_idx=node_index[curr_node_id],
                        amount=change_amount,
                        display_amount=change_amount,
                        flow_type=flow_type,
                        metadata={"section": section, "period_change": f"{prev_period} → {curr_period}"},
                    )
                )

        return FinancialGraph(
            nodes=nodes,
            links=links,
            period=f"{prev_period} → {curr_period}",
            currency=currency,
            statement_type=self.statement_type,
            metadata={"template": "multi_period_comparison", "periods": periods},
        )

    def _section_role(self, section: str) -> str:
        """Map a section to a palette role."""
        if section in ("revenue", "cash_inflow", "asset"):
            return "revenue"
        if section in ("expense", "cost", "cost_of_revenue", "operating_expenses", "tax", "cash_outflow", "liability"):
            return "operating_expenses"
        if section in ("profit", "net_income", "equity"):
            return "profit"
        return "other"
