from __future__ import annotations

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates._income_standard_parts import (
    AmountMap,
    SectionInfo,
    amount,
    assign_indices,
    section_info,
)
from finflow_sankey.templates._income_standard_sections import (
    add_cost_nodes,
    add_final_nodes,
    add_operating_nodes,
    add_revenue,
)


def build_standard_income_statement(df: pl.DataFrame) -> FinancialGraph:
    period = df["period"][0] if len(df) > 0 else None
    currency = df["currency"][0] if len(df) > 0 else None
    sections = section_info(df)
    amounts = _amounts(df, sections)
    levels = _levels(amounts)

    nodes: list[SankeyNode] = []
    links: list[SankeyLink] = []
    add_revenue(nodes, sections, amounts, levels)
    previous = add_cost_nodes(nodes, links, sections, amounts, levels)
    add_operating_nodes(nodes, links, sections, amounts, levels, previous)
    add_final_nodes(nodes, links, sections, amounts, levels)
    assign_indices(nodes, links)

    return FinancialGraph(
        nodes=nodes,
        links=links,
        period=period,
        currency=currency,
        statement_type="income_statement",
        metadata={"template": "income_statement"},
    )


def _amounts(df: pl.DataFrame, sections: SectionInfo) -> AmountMap:
    revenue = amount(sections, "revenue")
    cost = amount(sections, "cost_of_revenue") or amount(sections, "cost")
    opex = amount(sections, "operating_expenses") or amount(sections, "expense")
    tax = amount(sections, "tax")
    non_operating = amount(sections, "non_operating_items")
    profit = amount(sections, "profit")
    gross_profit = revenue - cost
    operating_income = gross_profit - opex
    raw_non_operating = (
        df.filter(df["section"] == "non_operating_items")["value"].sum()
        if "non_operating_items" in sections
        else 0.0
    )
    non_operating_is_income = raw_non_operating > 0
    computed_profit = operating_income - tax
    computed_profit = (
        computed_profit + non_operating
        if non_operating_is_income
        else computed_profit - non_operating
    )
    return {
        "revenue": revenue,
        "cost": cost,
        "opex": opex,
        "tax": tax,
        "non_operating": non_operating,
        "profit": profit or computed_profit,
        "gross_profit": gross_profit,
        "operating_income": operating_income,
        "non_operating_is_income": non_operating_is_income,
    }


def _levels(amounts: AmountMap) -> dict[str, int]:
    has_cogs = float(amounts["cost"]) > 0
    has_opex = float(amounts["opex"]) > 0
    if has_cogs and has_opex:
        return {
            "revenue": 0,
            "cost_of_revenue": 1,
            "gross_profit": 1,
            "operating_expenses": 2,
            "operating_income": 2,
            "tax": 3,
            "non_operating_items": 3,
            "net_income": 3,
        }
    if has_cogs:
        return {
            "revenue": 0,
            "cost_of_revenue": 1,
            "gross_profit": 1,
            "operating_income": 2,
            "tax": 3,
            "non_operating_items": 3,
            "net_income": 3,
        }
    if has_opex:
        return {
            "revenue": 0,
            "operating_expenses": 1,
            "operating_income": 1,
            "tax": 2,
            "non_operating_items": 2,
            "net_income": 2,
        }
    return {
        "revenue": 0,
        "operating_income": 1,
        "tax": 2,
        "non_operating_items": 2,
        "net_income": 2,
    }
