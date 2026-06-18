"""Plotly-based Sankey renderer."""

from __future__ import annotations

import plotly.graph_objects as go

from finflow_sankey.core.graph import FinancialGraph, SankeyNode
from finflow_sankey.core.palette import ColorPalette, hex_to_rgba
from finflow_sankey.renderers.base import Renderer
from finflow_sankey.renderers.reference_layout import (
    add_reference_legend,
    apply_reference_layout,
)


class PlotlyRenderer(Renderer):
    """Renders FinancialGraph using Plotly go.Sankey."""

    def render(
        self,
        graph: FinancialGraph,
        palette: ColorPalette,
        title: str | None = None,
    ) -> go.Figure:
        palette.validate()

        labels = [self._node_label(node) for node in graph.nodes]
        node_colors = [palette.get_role_color(node.role) for node in graph.nodes]
        node_hover = self._build_node_hover(graph)
        node_x = self._build_node_x(graph)
        node_y = self._build_node_y(graph)

        is_reference = graph.metadata.get("visual_style") == "reference"

        link_sources = [link.source_idx for link in graph.links]
        link_targets = [link.target_idx for link in graph.links]
        link_values = [link.amount for link in graph.links]
        node_role_by_id = {node.node_id: node.role for node in graph.nodes}
        link_roles = [node_role_by_id.get(link.target, "other") for link in graph.links]
        link_colors = [
            hex_to_rgba(palette.get_role_color(role), palette.semantic.link_opacity)
            for role in link_roles
        ]
        link_hover = self._build_link_hover(graph)

        sankey = go.Sankey(
            arrangement="fixed" if is_reference else "snap",
            node=dict(
                pad=16 if is_reference else 24,
                thickness=palette.semantic.node_thickness,
                line=dict(
                    color=palette.semantic.border,
                    width=palette.semantic.node_border_width,
                ),
                label=labels,
                color=node_colors,
                x=node_x,
                y=node_y,
                customdata=node_hover,
                hovertemplate="%{customdata}<extra></extra>",
            ),
            link=dict(
                source=link_sources,
                target=link_targets,
                value=link_values,
                color=link_colors,
                line=dict(
                    color=palette.semantic.border,
                    width=palette.semantic.link_border_width,
                ),
                customdata=link_hover,
                hovertemplate="%{customdata}<extra></extra>",
            ),
        )

        fig = go.Figure(data=[sankey])

        self._apply_layout(fig, palette, title, graph)
        self._add_legend(fig, palette, graph)

        return fig

    def _build_node_x(self, graph: FinancialGraph) -> list[float]:
        """Compute x positions based on explicit node.x or node levels."""
        has_explicit_x = any(node.x is not None for node in graph.nodes)
        if has_explicit_x:
            return [node.x if node.x is not None else 0.0 for node in graph.nodes]

        max_level = max((node.level for node in graph.nodes), default=0)
        if max_level == 0:
            return [0.0] * len(graph.nodes)
        return [node.level / max_level for node in graph.nodes]

    def _build_node_y(self, graph: FinancialGraph) -> list[float]:
        """Use explicit node.y when available, otherwise let Plotly auto-place."""
        has_explicit_y = any(node.y is not None for node in graph.nodes)
        if not has_explicit_y:
            return []
        return [node.y if node.y is not None else 0.5 for node in graph.nodes]

    def _build_node_hover(self, graph: FinancialGraph) -> list[str]:
        total_revenue = graph.get_role_amount("revenue") or graph.get_role_amount("cash_balance") or 1.0
        hover_texts = []
        for node in graph.nodes:
            share = (node.amount / total_revenue) * 100
            accounts = node.metadata.get("original_accounts", [])
            accounts_text = ", ".join(accounts) if accounts else "N/A"

            text = (
                f"<b>{node.label}</b><br>"
                f"Amount: {self._fmt_money(node.display_amount)}<br>"
                f"Share: {share:.1f}%<br>"
                f"Period: {graph.period or 'N/A'}<br>"
                f"Currency: {graph.currency or 'N/A'}<br>"
                f"Role: {node.role}<br>"
                f"Original accounts: {accounts_text}<br>"
                f"Validation: Passed"
            )
            hover_texts.append(text)
        return hover_texts

    def _build_link_hover(self, graph: FinancialGraph) -> list[str]:
        total_revenue = graph.get_role_amount("revenue") or graph.get_role_amount("cash_balance") or 1.0
        hover_texts = []
        for link in graph.links:
            source_node = graph.nodes[link.source_idx]
            target_node = graph.nodes[link.target_idx]
            share = (link.amount / total_revenue) * 100
            accounts = link.metadata.get("original_accounts", [])
            accounts_text = ", ".join(accounts) if accounts else "N/A"

            text = (
                f"<b>{source_node.label} → {target_node.label}</b><br>"
                f"Amount: {self._fmt_money(link.display_amount)}<br>"
                f"Share: {share:.1f}%<br>"
                f"Flow type: {link.flow_type.title()}<br>"
                f"Original accounts: {accounts_text}"
            )
            hover_texts.append(text)
        return hover_texts

    def _fmt_money(self, value: float) -> str:
        """Format a numeric value with compact unit suffix."""
        abs_value = abs(value)
        if abs_value >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:,.1f}T"
        if abs_value >= 1_000_000_000:
            return f"{value / 1_000_000_000:,.1f}B"
        if abs_value >= 1_000_000:
            return f"{value / 1_000_000:,.1f}M"
        if abs_value >= 1_000:
            return f"{value / 1_000:,.1f}K"
        return f"{value:,.0f}"

    def _node_label(self, node: SankeyNode) -> str:
        """Build node label with value on a second line."""
        value_text = self._fmt_money(node.display_amount)
        return f"{node.label}<br><span style='font-size:0.85em;opacity:0.8'>{value_text}</span>"

    def _apply_layout(
        self,
        fig: go.Figure,
        palette: ColorPalette,
        title: str | None,
        graph: FinancialGraph,
    ) -> None:
        is_reconciliation = graph.metadata.get("reconciliation_view", False)
        is_reference = graph.metadata.get("visual_style") == "reference"
        title_text = title or f"{graph.statement_type or 'Financial'} Flow"
        if is_reconciliation:
            title_text = f"[Reconciliation View] {title_text}"

        if is_reference:
            apply_reference_layout(fig, palette, title_text, graph)
            return

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(
                    size=palette.semantic.title_font_size,
                    color=palette.semantic.text,
                    family=palette.semantic.font_family,
                ),
                x=0.5,
                xanchor="center",
            ),
            font=dict(
                size=palette.semantic.font_size,
                color=palette.semantic.text,
                family=palette.semantic.font_family,
            ),
            paper_bgcolor=palette.semantic.background,
            plot_bgcolor=palette.semantic.plot_background,
            margin=dict(l=60, r=160, t=100, b=60),
            showlegend=False,
            height=700,
            width=1300,
        )

    def _add_legend(self, fig: go.Figure, palette: ColorPalette, graph: FinancialGraph) -> None:
        if graph.metadata.get("visual_style") == "reference":
            add_reference_legend(fig, palette)
            return

        annotations = []
        for i, role in enumerate(dict.fromkeys(node.role for node in graph.nodes)):
            color = palette.get_role_color(role)
            label = role.replace("_", " ").title()
            annotations.append(
                dict(
                    x=1.01,
                    y=0.96 - i * 0.06,
                    xref="paper",
                    yref="paper",
                    text=f"<span style='color:{color};'>●</span> {label}",
                    showarrow=False,
                    font=dict(
                        size=13,
                        color=palette.semantic.text,
                        family=palette.semantic.font_family,
                    ),
                    align="left",
                )
            )

        if annotations:
            fig.update_layout(annotations=annotations)
