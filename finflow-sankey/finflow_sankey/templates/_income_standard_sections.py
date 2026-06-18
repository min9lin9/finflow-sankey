from __future__ import annotations

from finflow_sankey.core.graph import SankeyLink, SankeyNode
from finflow_sankey.templates._income_standard_parts import (
    AmountMap,
    SectionInfo,
    accounts,
    add_link,
    add_node,
)


def add_revenue(
    nodes: list[SankeyNode],
    sections: SectionInfo,
    amounts: AmountMap,
    levels: dict[str, int],
) -> None:
    add_node(
        nodes,
        "revenue",
        "Revenue",
        "revenue",
        levels["revenue"],
        float(amounts["revenue"]),
        accounts(sections, "revenue"),
        0.5,
    )


def add_cost_nodes(
    nodes: list[SankeyNode],
    links: list[SankeyLink],
    sections: SectionInfo,
    amounts: AmountMap,
    levels: dict[str, int],
) -> list[str]:
    if float(amounts["cost"]) <= 0:
        return ["revenue"]
    cost_accounts = accounts(sections, "cost_of_revenue") or accounts(sections, "cost")
    add_node(
        nodes,
        "cost_of_revenue",
        "Cost of Revenue",
        "cost_of_revenue",
        levels["cost_of_revenue"],
        float(amounts["cost"]),
        cost_accounts,
        0.78,
    )
    add_link(links, "revenue", "cost_of_revenue", float(amounts["cost"]), "outflow")
    add_node(
        nodes,
        "gross_profit",
        "Gross Profit",
        "gross_profit",
        levels["gross_profit"],
        float(amounts["gross_profit"]),
        [],
        0.35,
    )
    add_link(links, "revenue", "gross_profit", float(amounts["gross_profit"]), "residual")
    return ["gross_profit"]


def add_operating_nodes(
    nodes: list[SankeyNode],
    links: list[SankeyLink],
    sections: SectionInfo,
    amounts: AmountMap,
    levels: dict[str, int],
    previous: list[str],
) -> None:
    if float(amounts["opex"]) > 0:
        opex_accounts = accounts(sections, "operating_expenses") or accounts(sections, "expense")
        add_node(
            nodes,
            "operating_expenses",
            "Operating Expenses",
            "operating_expenses",
            levels["operating_expenses"],
            float(amounts["opex"]),
            opex_accounts,
            0.78,
        )
        for source in previous:
            add_link(links, source, "operating_expenses", float(amounts["opex"]), "outflow")
    add_node(
        nodes,
        "operating_income",
        "Operating Income",
        "operating_income",
        levels["operating_income"],
        float(amounts["operating_income"]),
        [],
        0.35,
    )
    for source in previous:
        add_link(links, source, "operating_income", float(amounts["operating_income"]), "residual")


def add_final_nodes(
    nodes: list[SankeyNode],
    links: list[SankeyLink],
    sections: SectionInfo,
    amounts: AmountMap,
    levels: dict[str, int],
) -> None:
    if float(amounts["tax"]) > 0:
        add_node(
            nodes,
            "tax",
            "Tax",
            "tax",
            levels["tax"],
            float(amounts["tax"]),
            accounts(sections, "tax"),
            0.65,
        )
        add_link(links, "operating_income", "tax", float(amounts["tax"]), "outflow")
    if float(amounts["non_operating"]) > 0:
        add_non_operating_node(nodes, links, sections, amounts, levels)
    net_income_link = float(amounts["operating_income"]) - float(amounts["tax"])
    if bool(amounts["non_operating_is_income"]):
        net_income_link += float(amounts["non_operating"])
    add_node(
        nodes,
        "net_income",
        "Net Income",
        "net_income",
        levels["net_income"],
        float(amounts["profit"]),
        accounts(sections, "profit"),
        0.35,
    )
    add_link(links, "operating_income", "net_income", net_income_link, "residual")
    if bool(amounts["non_operating_is_income"]):
        add_link(
            links,
            "non_operating_items",
            "net_income",
            float(amounts["non_operating"]),
            "residual",
        )


def add_non_operating_node(
    nodes: list[SankeyNode],
    links: list[SankeyLink],
    sections: SectionInfo,
    amounts: AmountMap,
    levels: dict[str, int],
) -> None:
    is_income = bool(amounts["non_operating_is_income"])
    label = "Non-operating Income" if is_income else "Non-operating Items"
    y = 0.22 if is_income else 0.78
    add_node(
        nodes,
        "non_operating_items",
        label,
        "non_operating_items",
        levels["non_operating_items"],
        float(amounts["non_operating"]),
        accounts(sections, "non_operating_items"),
        y,
    )
    if not is_income:
        add_link(
            links,
            "operating_income",
            "non_operating_items",
            float(amounts["non_operating"]),
            "outflow",
        )
