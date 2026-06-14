"""Balance sheet reconciliation Sankey template."""

from __future__ import annotations

from typing import Any

import polars as pl

from finflow_sankey.core.graph import FinancialGraph, SankeyLink, SankeyNode
from finflow_sankey.templates.base import StatementTemplate


class BalanceSheetReconciliationTemplate(StatementTemplate):
    """Builds a Sankey graph for balance sheet reconciliation view."""

    statement_type = "balance_sheet_reconciliation"

    def required_roles(self) -> set[str]:
        # Require at least one asset, one liability, and equity sections.
        # Users can provide aggregate "asset"/"liability" or detailed sections.
        return {"asset", "liability", "equity"}

    def build(self, df: pl.DataFrame, **kwargs: Any) -> FinancialGraph:
        """
        Build balance sheet reconciliation Sankey.

        Layout: Assets on the left, Liabilities and Equity on the right.
        Expected sections:
            asset, current_asset, non_current_asset,
            liability, current_liability, non_current_liability,
            equity
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

        def _section_amount(section: str) -> float:
            return section_info.get(section, {}).get("amount", 0.0)

        def _section_accounts(section: str) -> list[str]:
            return section_info.get(section, {}).get("accounts", [])

        # Compute totals
        asset_total = (
            _section_amount("asset")
            + _section_amount("current_asset")
            + _section_amount("non_current_asset")
        )
        liability_total = (
            _section_amount("liability")
            + _section_amount("current_liability")
            + _section_amount("non_current_liability")
        )
        equity_total = _section_amount("equity")
        le_total = liability_total + equity_total

        # Left side: Assets
        nodes.append(
            SankeyNode(
                node_id="total_assets",
                label="Total Assets",
                role="asset",
                level=0,
                x=0.0,
                y=0.5,
                amount=asset_total,
                display_amount=asset_total,
                metadata={"section": "asset", "original_accounts": _section_accounts("asset")},
            )
        )

        if "current_asset" in section_info:
            nodes.append(
                SankeyNode(
                    node_id="current_assets",
                    label="Current Assets",
                    role="asset",
                    level=1,
                    x=0.25,
                    y=0.32,
                    amount=_section_amount("current_asset"),
                    display_amount=_section_amount("current_asset"),
                    metadata={
                        "section": "current_asset",
                        "original_accounts": _section_accounts("current_asset"),
                    },
                )
            )
            links.append(
                SankeyLink(
                    source="total_assets",
                    target="current_assets",
                    source_idx=0,
                    target_idx=len(nodes) - 1,
                    amount=_section_amount("current_asset"),
                    display_amount=_section_amount("current_asset"),
                    flow_type="reconciliation",
                    metadata={"section": "current_asset"},
                )
            )

        if "non_current_asset" in section_info:
            nodes.append(
                SankeyNode(
                    node_id="non_current_assets",
                    label="Non-current Assets",
                    role="asset",
                    level=1,
                    x=0.25,
                    y=0.68,
                    amount=_section_amount("non_current_asset"),
                    display_amount=_section_amount("non_current_asset"),
                    metadata={
                        "section": "non_current_asset",
                        "original_accounts": _section_accounts("non_current_asset"),
                    },
                )
            )
            links.append(
                SankeyLink(
                    source="total_assets",
                    target="non_current_assets",
                    source_idx=0,
                    target_idx=len(nodes) - 1,
                    amount=_section_amount("non_current_asset"),
                    display_amount=_section_amount("non_current_asset"),
                    flow_type="reconciliation",
                    metadata={"section": "non_current_asset"},
                )
            )

        # Right side: Liabilities and Equity
        nodes.append(
            SankeyNode(
                node_id="total_liabilities_and_equity",
                label="Total Liabilities and Equity",
                role="liability",
                level=0,
                x=1.0,
                y=0.5,
                amount=le_total,
                display_amount=le_total,
                metadata={
                    "section": "liability",
                    "original_accounts": (
                        _section_accounts("liability")
                        + _section_accounts("current_liability")
                        + _section_accounts("non_current_liability")
                        + _section_accounts("equity")
                    ),
                },
            )
        )

        right_sections = [
            ("liability", "Liabilities", "liability", 0.35),
            ("current_liability", "Current Liabilities", "liability", 0.28),
            ("non_current_liability", "Non-current Liabilities", "liability", 0.42),
            ("equity", "Equity", "equity", 0.65),
        ]

        # If aggregate liability is present without sub-sections, skip sub-sections
        has_aggregate_liability = "liability" in section_info
        has_detail_liability = "current_liability" in section_info or "non_current_liability" in section_info

        for section, label, role, y in right_sections:
            if section not in section_info:
                continue
            # Skip detail liability sections when only aggregate liability is provided
            if has_aggregate_liability and not has_detail_liability and section in ("current_liability", "non_current_liability"):
                continue

            nodes.append(
                SankeyNode(
                    node_id=section,
                    label=label,
                    role=role,
                    level=1,
                    x=0.75,
                    y=y,
                    amount=_section_amount(section),
                    display_amount=_section_amount(section),
                    metadata={"section": section, "original_accounts": _section_accounts(section)},
                )
            )
            links.append(
                SankeyLink(
                    source="total_liabilities_and_equity",
                    target=section,
                    source_idx=0,  # updated below
                    target_idx=len(nodes) - 1,
                    amount=_section_amount(section),
                    display_amount=_section_amount(section),
                    flow_type="reconciliation",
                    metadata={"section": section},
                )
            )

        # Update source/target indices correctly
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
            metadata={"template": "balance_sheet_reconciliation", "reconciliation_view": True},
        )
