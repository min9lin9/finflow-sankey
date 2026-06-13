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

        # Aggregate by section
        section_info = {}
        for section in df["section"].unique().to_list():
            section_df = df.filter(df["section"] == section)
            section_info[section] = {
                "amount": section_df["sankey_value"].sum(),
                "accounts": section_df["account"].to_list(),
            }

        def _amount(section: str) -> float:
            return section_info.get(section, {}).get("amount", 0.0)

        def _accounts(section: str) -> list[str]:
            return section_info.get(section, {}).get("accounts", [])

        # Normalize section aliases to canonical names
        revenue_amount = _amount("revenue")
        cost_of_revenue_amount = _amount("cost_of_revenue") or _amount("cost")
        operating_expenses_amount = _amount("operating_expenses") or _amount("expense")
        tax_amount = _amount("tax")
        non_operating_amount = _amount("non_operating_items")
        profit_amount = _amount("profit")

        # Intermediate aggregates
        gross_profit_amount = revenue_amount - cost_of_revenue_amount
        operating_income_amount = gross_profit_amount - operating_expenses_amount
        net_income_computed = operating_income_amount - tax_amount - non_operating_amount
        if profit_amount == 0.0:
            profit_amount = net_income_computed

        nodes: list[SankeyNode] = []
        links: list[SankeyLink] = []

        def add_node(
            node_id: str,
            label: str,
            role: str,
            level: int,
            amount: float,
            accounts: list[str],
            y: float | None = None,
        ) -> SankeyNode:
            node = SankeyNode(
                node_id=node_id,
                label=label,
                role=role,
                level=level,
                amount=amount,
                display_amount=amount,
                x=None,
                y=y,
                metadata={"section": node_id, "original_accounts": accounts},
            )
            nodes.append(node)
            return node

        def add_link(source: str, target: str, amount: float, flow_type: str = "flow", accounts: list[str] | None = None) -> None:
            links.append(
                SankeyLink(
                    source=source,
                    target=target,
                    source_idx=0,
                    target_idx=0,
                    amount=amount,
                    display_amount=amount,
                    flow_type=flow_type,
                    metadata={"original_accounts": accounts or []},
                )
            )

        # Level 0: Revenue
        add_node("revenue", "Revenue", "revenue", 0, revenue_amount, _accounts("revenue"), y=0.5)

        # Level 1: Cost of Revenue + Gross Profit
        if cost_of_revenue_amount > 0:
            add_node(
                "cost_of_revenue",
                "Cost of Revenue",
                "cost_of_revenue",
                1,
                cost_of_revenue_amount,
                _accounts("cost_of_revenue") or _accounts("cost"),
                y=0.78,
            )
            add_link("revenue", "cost_of_revenue", cost_of_revenue_amount, "outflow")

        add_node(
            "gross_profit",
            "Gross Profit",
            "gross_profit",
            1,
            gross_profit_amount,
            [],
            y=0.35,
        )
        add_link("revenue", "gross_profit", gross_profit_amount, "residual")

        # Level 2: Operating Expenses + Operating Income
        if operating_expenses_amount > 0:
            add_node(
                "operating_expenses",
                "Operating Expenses",
                "operating_expenses",
                2,
                operating_expenses_amount,
                _accounts("operating_expenses") or _accounts("expense"),
                y=0.78,
            )
            add_link("gross_profit", "operating_expenses", operating_expenses_amount, "outflow")

        add_node(
            "operating_income",
            "Operating Income",
            "operating_income",
            2,
            operating_income_amount,
            [],
            y=0.35,
        )
        add_link("gross_profit", "operating_income", operating_income_amount, "residual")

        # Level 3: Non-operating + Tax + Net Income
        if non_operating_amount > 0:
            add_node(
                "non_operating_items",
                "Non-operating Items",
                "non_operating_items",
                3,
                non_operating_amount,
                _accounts("non_operating_items"),
                y=0.78,
            )
            add_link("operating_income", "non_operating_items", non_operating_amount, "outflow")

        if tax_amount > 0:
            add_node(
                "tax",
                "Tax",
                "tax",
                3,
                tax_amount,
                _accounts("tax"),
                y=0.65,
            )
            add_link("operating_income", "tax", tax_amount, "outflow")

        add_node(
            "net_income",
            "Net Income",
            "net_income",
            3,
            profit_amount,
            _accounts("profit"),
            y=0.35,
        )
        add_link("operating_income", "net_income", profit_amount, "residual")

        # Update indices
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
