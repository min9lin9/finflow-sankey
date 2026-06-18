"""Reference income statement layout with detailed account nodes.

This is a private module used by `IncomeStatementTemplate` when
`layout="reference"` is requested.
"""

from __future__ import annotations

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates._income_reference_parts import (
    accounts,
    add_link,
    add_node,
    amount,
    assign_indices,
    build_section_info,
    weighted_spread,
)


def build_reference_income_statement(df: pl.DataFrame) -> FinancialGraph:
    """Build a reference-style income statement Sankey graph."""
    period = df["period"][0] if len(df) > 0 else None
    currency = df["currency"][0] if len(df) > 0 else None

    section_info = build_section_info(df)
    revenue = amount(section_info, "revenue")
    cost = amount(section_info, "cost_of_revenue") or amount(section_info, "cost")
    opex = amount(section_info, "operating_expenses") or amount(section_info, "expense")
    tax = amount(section_info, "tax")
    non_op = amount(section_info, "non_operating_items")
    profit = amount(section_info, "profit")

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

    revenue_df = df.filter(df["section"] == "revenue")
    has_revenue_details = len(revenue_df) > 1
    revenue_x = 0.25 if has_revenue_details else 0.0
    add_node(
        nodes,
        "revenue",
        "Total Revenue" if has_revenue_details else "Revenue",
        "revenue",
        1 if has_revenue_details else 0,
        revenue,
        accounts(section_info, "revenue"),
        revenue_x,
        0.48,
    )
    if has_revenue_details:
        revenue_values = [float(row["sankey_value"]) for row in revenue_df.iter_rows(named=True)]
        y_positions = weighted_spread(revenue_values, 0.30, 0.66)
        for index, row in enumerate(revenue_df.iter_rows(named=True)):
            node_id = f"revenue_detail_{index}"
            account = str(row["account"])
            value = float(row["sankey_value"])
            add_node(
                nodes,
                node_id,
                account,
                "revenue",
                0,
                value,
                [account],
                0.0,
                y_positions[index],
            )
            add_link(links, node_id, "revenue", value, account_names=[account])

    previous = ["revenue"]
    if cost > 0:
        cost_accounts = accounts(section_info, "cost_of_revenue") or accounts(section_info, "cost")
        label = cost_accounts[0] if len(cost_accounts) == 1 else "Cost of Revenue"
        add_node(
            nodes,
            "cost_of_revenue",
            label,
            "cost_of_revenue",
            2,
            cost,
            cost_accounts,
            0.5,
            0.78,
        )
        add_link(links, "revenue", "cost_of_revenue", cost, "outflow", cost_accounts)
        add_node(
            nodes,
            "gross_profit",
            "Gross Profit",
            "gross_profit",
            2,
            gross_profit,
            [],
            0.5,
            0.28,
        )
        add_link(links, "revenue", "gross_profit", gross_profit, "residual")
        previous = ["gross_profit"]

    if opex > 0:
        opex_accounts = accounts(section_info, "operating_expenses") or accounts(
            section_info,
            "expense",
        )
        x = 0.72 if previous == ["gross_profit"] else 0.5
        add_node(
            nodes,
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
            add_link(links, source, "operating_expenses", opex, "outflow", opex_accounts)

        opex_df = df.filter(pl.col("section").is_in(["operating_expenses", "expense"]))
        if len(opex_df) > 1:
            opex_values = [float(row["sankey_value"]) for row in opex_df.iter_rows(named=True)]
            y_positions = weighted_spread(opex_values, 0.46, 0.86)
            for index, row in enumerate(opex_df.iter_rows(named=True)):
                node_id = f"operating_expense_detail_{index}"
                account = str(row["account"])
                value = float(row["sankey_value"])
                add_node(
                    nodes,
                    node_id,
                    account,
                    "operating_expenses",
                    4 if previous == ["gross_profit"] else 3,
                    value,
                    [account],
                    0.92,
                    y_positions[index],
                )
                add_link(links, "operating_expenses", node_id, value, "outflow", [account])

    op_income_x = 0.72 if previous == ["gross_profit"] else 0.5
    op_income_level = 4 if (previous == ["gross_profit"] and opex > 0 and len(df.filter(pl.col("section").is_in(["operating_expenses", "expense"]))) > 1) else (3 if previous == ["gross_profit"] else 2)
    add_node(
        nodes,
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
        add_link(links, source, "operating_income", operating_income, "residual")

    if tax > 0:
        tax_accounts = accounts(section_info, "tax")
        add_node(
            nodes,
            "tax",
            "Tax",
            "tax",
            5,
            tax,
            tax_accounts,
            0.92,
            0.48,
        )
        add_link(links, "operating_income", "tax", tax, "outflow", tax_accounts)

    if non_op > 0:
        label = "Non-operating Income" if non_op_is_income else "Non-operating Items"
        y = 0.12 if non_op_is_income else 0.86
        add_node(
            nodes,
            "non_operating_items",
            label,
            "non_operating_items",
            5,
            non_op,
            accounts(section_info, "non_operating_items"),
            0.92,
            y,
        )
        if not non_op_is_income:
            add_link(
                links,
                "operating_income",
                "non_operating_items",
                non_op,
                "outflow",
                accounts(section_info, "non_operating_items"),
            )

    net_income_link = operating_income - tax
    if non_op_is_income:
        net_income_link += non_op

    add_node(
        nodes,
        "net_income",
        "Net Income",
        "net_income",
        5,
        profit,
        accounts(section_info, "profit"),
        1.0,
        0.24,
    )
    add_link(links, "operating_income", "net_income", net_income_link, "residual")
    if non_op_is_income:
        add_link(links, "non_operating_items", "net_income", non_op, "residual")

    assign_indices(nodes, links)

    return FinancialGraph(
        nodes=nodes,
        links=links,
        period=period,
        currency=currency,
        statement_type="income_statement",
        metadata={"template": "income_statement", "visual_style": "reference"},
    )
