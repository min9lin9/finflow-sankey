from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from finflow_sankey.core.graph import SankeyLink, SankeyNode


@dataclass(frozen=True)
class SectionInfo:
    amount: float
    accounts: list[str]


def build_section_info(df: pl.DataFrame) -> dict[str, SectionInfo]:
    result: dict[str, SectionInfo] = {}
    for section in df["section"].unique().to_list():
        section_df = df.filter(df["section"] == section)
        result[section] = SectionInfo(
            amount=float(section_df["sankey_value"].sum()),
            accounts=section_df["account"].to_list(),
        )
    return result


def amount(section_info: dict[str, SectionInfo], section: str) -> float:
    info = section_info.get(section)
    return info.amount if info is not None else 0.0


def accounts(section_info: dict[str, SectionInfo], section: str) -> list[str]:
    info = section_info.get(section)
    return info.accounts if info is not None else []


def add_node(
    nodes: list[SankeyNode],
    node_id: str,
    label: str,
    role: str,
    level: int,
    node_amount: float,
    account_names: list[str],
    x: float,
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
            x=x,
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


def weighted_spread(
    values: list[float],
    start: float,
    end: float,
    min_gap: float = 0.06,
) -> list[float]:
    if not values:
        return []
    if len(values) == 1:
        return [(start + end) / 2]

    total = max(sum(values), 1e-9)
    weights = [max(value, total * 0.02) / total for value in values]
    cumulative = [0.0]
    for weight in weights[:-1]:
        cumulative.append(cumulative[-1] + weight)

    positions = [
        start + (end - start) * (offset + weight / 2)
        for offset, weight in zip(cumulative, weights)
    ]
    return _enforce_min_gap(positions, start, end, min_gap)


def assign_indices(nodes: list[SankeyNode], links: list[SankeyLink]) -> None:
    node_index = {node.node_id: index for index, node in enumerate(nodes)}
    for link in links:
        link.source_idx = node_index[link.source]
        link.target_idx = node_index[link.target]


def _enforce_min_gap(
    positions: list[float],
    start: float,
    end: float,
    min_gap: float,
) -> list[float]:
    adjusted = positions[:]
    for _ in range(10):
        previous = adjusted[:]
        for index in range(1, len(adjusted)):
            gap = adjusted[index] - adjusted[index - 1]
            if gap < min_gap:
                push = (min_gap - gap) / 2
                adjusted[index - 1] = max(start, adjusted[index - 1] - push)
                adjusted[index] = min(end, adjusted[index] + push)
        if adjusted == previous:
            break
    return [max(start, min(end, position)) for position in adjusted]
