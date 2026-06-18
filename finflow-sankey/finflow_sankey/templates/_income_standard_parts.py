from __future__ import annotations

from typing import Union

import polars as pl

from finflow_sankey.core.graph import SankeyLink, SankeyNode


SectionInfo = dict[str, dict[str, Union[list[str], float]]]
AmountMap = dict[str, Union[float, bool]]


def section_info(df: pl.DataFrame) -> SectionInfo:
    result: SectionInfo = {}
    for section in df["section"].unique().to_list():
        section_df = df.filter(df["section"] == section)
        result[section] = {
            "amount": section_df["sankey_value"].sum(),
            "accounts": section_df["account"].to_list(),
        }
    return result


def amount(info: SectionInfo, section: str) -> float:
    return float(info.get(section, {}).get("amount", 0.0))


def accounts(info: SectionInfo, section: str) -> list[str]:
    value = info.get(section, {}).get("accounts", [])
    return value if isinstance(value, list) else []


def add_node(
    nodes: list[SankeyNode],
    node_id: str,
    label: str,
    role: str,
    level: int,
    node_amount: float,
    account_names: list[str],
    y: float,
) -> None:
    nodes.append(
        SankeyNode(
            node_id=node_id,
            label=label,
            role=role,
            level=level,
            amount=node_amount,
            display_amount=node_amount,
            x=None,
            y=y,
            metadata={"section": node_id, "original_accounts": account_names},
        )
    )


def add_link(
    links: list[SankeyLink],
    source: str,
    target: str,
    link_amount: float,
    flow_type: str = "flow",
    account_names: list[str] | None = None,
) -> None:
    links.append(
        SankeyLink(
            source=source,
            target=target,
            source_idx=0,
            target_idx=0,
            amount=link_amount,
            display_amount=link_amount,
            flow_type=flow_type,
            metadata={"original_accounts": account_names or []},
        )
    )


def assign_indices(nodes: list[SankeyNode], links: list[SankeyLink]) -> None:
    node_index = {node.node_id: index for index, node in enumerate(nodes)}
    for link in links:
        link.source_idx = node_index[link.source]
        link.target_idx = node_index[link.target]
