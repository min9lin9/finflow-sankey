"""Reference income statement layout with detailed account nodes.

This is a private module used by `IncomeStatementTemplate` when
`layout="reference"` is requested.
"""

from __future__ import annotations

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode


def build_reference_income_statement(df: pl.DataFrame) -> FinancialGraph:
    """Build a reference-style income statement Sankey graph."""
    period = df["period"][0] if len(df) > 0 else None
    currency = df["currency"][0] if len(df) > 0 else None

    # Aggregate sections
    section_info: dict[str, dict[str, list[str] | float]] = {}
    for section in df["section"].unique().to_list():
        section_df = df.filter(df["section"] == section)
        section_info[section] = {
            "amount": float(section_df["sankey_value"].sum()),
            "accounts": section_df["account"].to_list(),
        }

    def _amount(section: str) -> float:
        return float(section_info.get(section, {}).get("amount", 0.0))

    def _accounts(section: str) -> list[str]:
        return section_info.get(section, {}).get("accounts", [])  # type: ignore[return-value]

    revenue = _amount("revenue")
    cost = _amount("cost_of_revenue") or _amount("cost")
    opex = _amount("operating_expenses") or _amount("expense")
    tax = _amount("tax")
    non_op = _amount("non_operating_items")
    profit = _amount("profit")

    gross_profit = revenue - cost
    operating_income = gross_profit - opex

    raw_non_op = (
        df.filter(df["section"] == "non_operating_items")["value"].sum()
        if "non_operating_items" in section_info
        else 0.0
    )
    non_op_is_income = raw_non_op > 0

    computed_profit = operating_income - tax
    computed_profit += non_op if non_op_is_income else -non_op
    profit = profit or computed_profit

    nodes: list[SankeyNode] = []
    links: list[SankeyLink] = []

    def add_node(
        node_id: str,
        label: str,
        role: str,
        level: int,
        amount: float,
        account_names: list[str],
        x: float,
        y: float,
    ) -> SankeyNode:
        node = SankeyNode(
            node_id=node_id,
            label=label,
            role=role,
            level=level,
            amount=amount,
            display_amount=amount,
            x=x,
            y=y,
            metadata={"section": node_id, "original_accounts": account_names},
        )
        nodes.append(node)
        return node

    def add_link(
        source: str,
        target: str,
        amount: float,
        flow_type: str = "flow",
        account_names: list[str] | None = None,
    ) -> None:
        links.append(
            SankeyLink(
                source=source,
                target=target,
                source_idx=0,
                target_idx=0,
                amount=amount,
                display_amount=amount,
                flow_type=flow_type,
                metadata={"original_accounts": account_names or []},
            )
        )

    def spread_y(count: int, start: float, end: float) -> list[float]:
        if count <= 1:
            return [(start + end) / 2]
        step = (end - start) / (count - 1)
        return [start + i * step for i in range(count)]

    # Revenue detail nodes
    revenue_df = df.filter(df["section"] == "revenue")
    has_revenue_details = len(revenue_df) > 1
    revenue_x = 0.25 if has_revenue_details else 0.0
    add_node(
        "revenue",
        "Total Revenue" if has_revenue_details else "Revenue",
        "revenue",
        1 if has_revenue_details else 0,
        revenue,
        _accounts("revenue"),
        revenue_x,
        0.48,
    )
    if has_revenue_details:
        y_positions = spread_y(len(revenue_df), 0.36, 0.66)
        for index, row in enumerate(revenue_df.iter_rows(named=True)):
            node_id = f"revenue_detail_{index}"
            account = str(row["account"])
            value = float(row["sankey_value"])
            add_node(
                node_id,
                account,
                "revenue",
                0,
                value,
                [account],
                0.0,
                y_positions[index],
            )
            add_link(node_id, "revenue", value, account_names=[account])

    # Cost of Revenue + Gross Profit
    previous = ["revenue"]
    if cost > 0:
        cost_accounts = _accounts("cost_of_revenue") or _accounts("cost")
        label = cost_accounts[0] if len(cost_accounts) == 1 else "Cost of Revenue"
        add_node(
            "cost_of_revenue",
            label,
            "cost_of_revenue",
            2,
            cost,
            cost_accounts,
            0.5,
            0.78,
        )
        add_link("revenue", "cost_of_revenue", cost, "outflow", cost_accounts)
        add_node(
            "gross_profit",
            "Gross Profit",
            "gross_profit",
            2,
            gross_profit,
            [],
            0.5,
            0.28,
        )
        add_link("revenue", "gross_profit", gross_profit, "residual")
        previous = ["gross_profit"]

    # Operating Expenses + Operating Income
    if opex > 0:
        opex_accounts = _accounts("operating_expenses") or _accounts("expense")
        x = 0.72 if previous == ["gross_profit"] else 0.5
        add_node(
            "operating_expenses",
            "Operating Expenses",
            "operating_expenses",
            3 if previous == ["gross_profit"] else 2,
            opex,
            opex_accounts,
            x,
            0.62,
        )
        for source in previous:
            add_link(source, "operating_expenses", opex, "outflow", opex_accounts)

        opex_df = df.filter(pl.col("section").is_in(["operating_expenses", "expense"]))
        if len(opex_df) > 1:
            y_positions = spread_y(len(opex_df), 0.46, 0.78)
            for index, row in enumerate(opex_df.iter_rows(named=True)):
                node_id = f"operating_expense_detail_{index}"
                account = str(row["account"])
                value = float(row["sankey_value"])
                add_node(
                    node_id,
                    account,
                    "operating_expenses",
                    4 if previous == ["gross_profit"] else 3,
                    value,
                    [account],
                    0.92,
                    y_positions[index],
                )
                add_link("operating_expenses", node_id, value, "outflow", [account])

    op_income_x = 0.72 if previous == ["gross_profit"] else 0.5
    op_income_level = 4 if (previous == ["gross_profit"] and opex > 0 and len(df.filter(pl.col("section").is_in(["operating_expenses", "expense"]))) > 1) else (3 if previous == ["gross_profit"] else 2)
    add_node(
        "operating_income",
        "Operating Income",
        "operating_income",
        op_income_level,
        operating_income,
        [],
        op_income_x,
        0.24,
    )
    for source in previous:
        add_link(source, "operating_income", operating_income, "residual")

    # Tax / Non-operating + Net Income
    if tax > 0:
        tax_accounts = _accounts("tax")
        add_node(
            "tax",
            "Tax",
            "tax",
            5,
            tax,
            tax_accounts,
            0.92,
            0.48,
        )
        add_link("operating_income", "tax", tax, "outflow", tax_accounts)

    if non_op > 0:
        label = "Non-operating Income" if non_op_is_income else "Non-operating Items"
        y = 0.12 if non_op_is_income else 0.86
        add_node(
            "non_operating_items",
            label,
            "non_operating_items",
            5,
            non_op,
            _accounts("non_operating_items"),
            0.92,
            y,
        )
        if not non_op_is_income:
            add_link(
                "operating_income",
                "non_operating_items",
                non_op,
                "outflow",
                _accounts("non_operating_items"),
            )

    net_income_link = operating_income - tax
    if non_op_is_income:
        net_income_link += non_op

    add_node(
        "net_income",
        "Net Income",
        "net_income",
        5,
        profit,
        _accounts("profit"),
        1.0,
        0.24,
    )
    add_link("operating_income", "net_income", net_income_link, "residual")
    if non_op_is_income:
        add_link("non_operating_items", "net_income", non_op, "residual")

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
        statement_type="income_statement",
        metadata={"template": "income_statement", "visual_style": "reference"},
    )
