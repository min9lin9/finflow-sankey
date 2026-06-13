"""Income statement Sankey template."""

from __future__ import annotations

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates.base import StatementTemplate


class IncomeStatementTemplate(StatementTemplate):
    """Builds a Sankey graph for income statement flow."""

    statement_type = "income_statement"

    def required_roles(self) -> set[str]:
        return {"revenue", "profit"}

    def build(self, df: pl.DataFrame) -> FinancialGraph:
        """
        Build income statement Sankey.

        Expected sections: revenue, cost, cost_of_revenue, expense,
        operating_expenses, tax, non_operating_items, profit
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

        # Ensure revenue exists
        revenue_amount = section_info.get("revenue", {}).get("amount", 0.0)

        # Create revenue node
        revenue_accounts = _section_accounts("revenue")
        nodes.append(
            SankeyNode(
                node_id="revenue",
                label="Revenue",
                role="revenue",
                level=0,
                amount=revenue_amount,
                display_amount=revenue_amount,
                metadata={"section": "revenue", "original_accounts": revenue_accounts},
            )
        )

        # Create expense nodes and links from revenue
        expense_sections = {
            "cost_of_revenue": "Cost of Revenue",
            "cost": "Cost of Revenue",
            "operating_expenses": "Operating Expenses",
            "expense": "Operating Expenses",
            "tax": "Tax",
            "non_operating_items": "Non-operating Items",
        }

        for section, label in expense_sections.items():
            if section not in section_info:
                continue

            amount = section_info[section]["amount"]
            node_id = section.replace(" ", "_").lower()
            accounts = _section_accounts(section)

            nodes.append(
                SankeyNode(
                    node_id=node_id,
                    label=label,
                    role=section if section != "cost" else "cost_of_revenue",
                    level=1,
                    amount=amount,
                    display_amount=amount,
                    metadata={"section": section, "original_accounts": accounts},
                )
            )

            links.append(
                SankeyLink(
                    source="revenue",
                    target=node_id,
                    source_idx=0,
                    target_idx=len(nodes) - 1,
                    amount=amount,
                    display_amount=amount,
                    flow_type="outflow",
                    metadata={"section": section, "original_accounts": accounts},
                )
            )

        # Create net income / profit node
        profit_amount = section_info.get("profit", {}).get("amount", revenue_amount)
        if "profit" not in section_info:
            # Compute as residual
            expenses = sum(
                v["amount"] for k, v in section_info.items() if k != "revenue" and k != "profit"
            )
            profit_amount = revenue_amount - expenses

        profit_accounts = _section_accounts("profit")
        nodes.append(
            SankeyNode(
                node_id="net_income",
                label="Net Income",
                role="net_income",
                level=2,
                amount=profit_amount,
                display_amount=profit_amount,
                metadata={"section": "profit", "original_accounts": profit_accounts},
            )
        )
        profit_idx = len(nodes) - 1

        # Link revenue to profit
        links.append(
            SankeyLink(
                source="revenue",
                target="net_income",
                source_idx=0,
                target_idx=profit_idx,
                amount=profit_amount,
                display_amount=profit_amount,
                flow_type="residual",
                metadata={
                    "section": "profit",
                    "original_accounts": revenue_accounts + profit_accounts,
                },
            )
        )

        # Update source/target indices
        node_index = {node.node_id: i for i, node in enumerate(nodes)}
        for link in links:
            link.source_idx = node_index[link.source]
            link.target_idx = node_index[link.target]

        return FinancialGraph(
            nodes=nodes,
            links=links,
            period=period,
            currency=currency,
            statement_type=self.statement_type,
            metadata={"template": "income_statement"},
        )
