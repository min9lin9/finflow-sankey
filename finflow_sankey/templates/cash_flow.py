"""Cash flow statement Sankey template."""

from __future__ import annotations

from typing import Any

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates.base import StatementTemplate


class CashFlowStatementTemplate(StatementTemplate):
    """Builds a Sankey graph for cash flow statement bridge."""

    statement_type = "cash_flow_statement"

    def required_roles(self) -> set[str]:
        return {"beginning_cash", "ending_cash"}

    def build(self, df: pl.DataFrame, **kwargs: Any) -> FinancialGraph:
        """
        Build cash flow statement Sankey.

        Expected sections:
            beginning_cash, operating_cash_flow, investing_cash_flow,
            financing_cash_flow, fx_effect, ending_cash
        """
        period = df["period"][0] if len(df) > 0 else None
        currency = df["currency"][0] if len(df) > 0 else None

        nodes: list[SankeyNode] = []
        links: list[SankeyLink] = []

        # Aggregate by section
        section_info = {}
        for section in df["section"].unique().to_list():
            section_df = df.filter(df["section"] == section)
            section_info[section] = {
                "amount": section_df["sankey_value"].sum(),
                "accounts": section_df["account"].to_list(),
            }

        def _section_accounts(section: str) -> list[str]:
            return section_info.get(section, {}).get("accounts", [])

        # Section definitions with labels and vertical positions
        sections = [
            ("beginning_cash", "Beginning Cash", 0.5),
            ("operating_cash_flow", "Operating Cash Flow", 0.18),
            ("investing_cash_flow", "Investing Cash Flow", 0.39),
            ("financing_cash_flow", "Financing Cash Flow", 0.61),
            ("fx_effect", "FX Effect", 0.82),
            ("ending_cash", "Ending Cash", 0.5),
        ]

        for section, label, y in sections:
            amount = section_info.get(section, {}).get("amount", 0.0)
            node_id = section
            accounts = _section_accounts(section)

            # Determine role from original value sign for cash flow sections
            if section in ("beginning_cash", "ending_cash"):
                role = "cash_balance"
            else:
                raw_value = df.filter(df["section"] == section)["value"].sum()
                role = "cash_inflow" if raw_value >= 0 else "cash_outflow"

            if section == "beginning_cash":
                level = 0
            elif section == "ending_cash":
                level = 2
            else:
                level = 1

            nodes.append(
                SankeyNode(
                    node_id=node_id,
                    label=label,
                    role=role,
                    level=level,
                    amount=amount,
                    display_amount=amount,
                    x=None,
                    y=y,
                    metadata={"section": section, "original_accounts": accounts},
                )
            )

        node_index = {node.node_id: i for i, node in enumerate(nodes)}

        # Beginning cash → each cash flow → ending cash
        # We route through intermediate nodes: beginning → flows, flows → ending
        # To make a clean Sankey, link each flow to ending cash directly
        # and beginning cash to ending cash via the flows.

        # First, beginning cash to each flow
        flow_sections = [
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_effect",
        ]

        for section in flow_sections:
            amount = section_info.get(section, {}).get("amount", 0.0)
            accounts = _section_accounts(section)
            if amount == 0.0:
                continue

            links.append(
                SankeyLink(
                    source="beginning_cash",
                    target=section,
                    source_idx=node_index["beginning_cash"],
                    target_idx=node_index[section],
                    amount=amount,
                    display_amount=amount,
                    flow_type="cash_flow",
                    metadata={"section": section, "original_accounts": accounts},
                )
            )

        # Then each flow to ending cash
        for section in flow_sections:
            amount = section_info.get(section, {}).get("amount", 0.0)
            accounts = _section_accounts(section)
            if amount == 0.0:
                continue

            links.append(
                SankeyLink(
                    source=section,
                    target="ending_cash",
                    source_idx=node_index[section],
                    target_idx=node_index["ending_cash"],
                    amount=amount,
                    display_amount=amount,
                    flow_type="cash_flow",
                    metadata={"section": section, "original_accounts": accounts},
                )
            )

        return FinancialGraph(
            nodes=nodes,
            links=links,
            period=period,
            currency=currency,
            statement_type=self.statement_type,
            metadata={"template": "cash_flow_statement"},
        )
