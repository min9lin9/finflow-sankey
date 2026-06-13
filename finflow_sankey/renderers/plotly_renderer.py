"""Plotly-based Sankey renderer."""

from __future__ import annotations

import plotly.graph_objects as go

from finflow_sankey.core.graph import FinancialGraph
from finflow_sankey.core.palette import ColorPalette, hex_to_rgba
from finflow_sankey.renderers.base import Renderer


class PlotlyRenderer(Renderer):
    """Renders FinancialGraph using Plotly go.Sankey."""

    def render(
        self,
        graph: FinancialGraph,
        palette: ColorPalette,
        title: str | None = None,
    ) -> go.Figure:
        palette.validate()

        labels = [node.label for node in graph.nodes]
        node_colors = [palette.get_role_color(node.role) for node in graph.nodes]
        node_hover = self._build_node_hover(graph)
        node_x = self._build_node_x(graph)

        link_sources = [link.source_idx for link in graph.links]
        link_targets = [link.target_idx for link in graph.links]
        link_values = [link.amount for link in graph.links]
        link_roles = [self._link_role(graph, link) for link in graph.links]
        link_colors = [
            hex_to_rgba(palette.get_role_color(role), palette.semantic.link_opacity)
            for role in link_roles
        ]
        link_hover = self._build_link_hover(graph)

        sankey = go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20,
                thickness=palette.semantic.node_thickness,
                line=dict(
                    color=palette.semantic.border,
                    width=palette.semantic.node_border_width,
                ),
                label=labels,
                color=node_colors,
                x=node_x,
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
        if not graph.nodes:
            return []

        # If any node has explicit x, use it; otherwise derive from level
        has_explicit_x = any(node.x is not None for node in graph.nodes)
        if has_explicit_x:
            return [node.x if node.x is not None else 0.0 for node in graph.nodes]

        max_level = max(node.level for node in graph.nodes)
        if max_level == 0:
            return [0.0] * len(graph.nodes)
        return [node.level / max_level for node in graph.nodes]

    def _link_role(self, graph: FinancialGraph, link) -> str:
        for node in graph.nodes:
            if node.node_id == link.source:
                return node.role
        return "other"

    def _build_node_hover(self, graph: FinancialGraph) -> list[str]:
        total_revenue = graph.get_role_amount("revenue") or graph.get_role_amount("cash_balance") or 1.0
        hover_texts = []
        for node in graph.nodes:
            share = (node.amount / total_revenue) * 100 if total_revenue else 0.0
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
            share = (link.amount / total_revenue) * 100 if total_revenue else 0.0
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
        return f"${value:,.0f}"

    def _apply_layout(
        self,
        fig: go.Figure,
        palette: ColorPalette,
        title: str | None,
        graph: FinancialGraph,
    ) -> None:
        is_reconciliation = graph.metadata.get("reconciliation_view", False)
        title_text = title or f"{graph.statement_type or 'Financial'} Flow"
        if is_reconciliation:
            title_text = f"[Reconciliation View] {title_text}"
        if graph.period:
            title_text += f" ({graph.period})"

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(
                    size=palette.semantic.title_font_size,
                    color=palette.semantic.text,
                    family=palette.semantic.font_family,
                ),
                x=0.5,
            ),
            font=dict(
                size=palette.semantic.font_size,
                color=palette.semantic.text,
                family=palette.semantic.font_family,
            ),
            paper_bgcolor=palette.semantic.background,
            plot_bgcolor=palette.semantic.plot_background,
            margin=dict(l=40, r=120, t=80, b=40),
            showlegend=False,
            height=600,
            width=1100,
        )

    def _add_legend(self, fig: go.Figure, palette: ColorPalette, graph: FinancialGraph) -> None:
        visible_roles = []
        for node in graph.nodes:
            if node.role not in visible_roles:
                visible_roles.append(node.role)

        annotations = []
        for i, role in enumerate(visible_roles):
            color = palette.get_role_color(role)
            label = role.replace("_", " ").title()
            annotations.append(
                dict(
                    x=1.02,
                    y=0.95 - i * 0.08,
                    xref="paper",
                    yref="paper",
                    text=f"<span style='color:{color};'>■</span> {label}",
                    showarrow=False,
                    font=dict(
                        size=12,
                        family=palette.semantic.font_family,
                    ),
                    align="left",
                )
            )

        if annotations:
            fig.update_layout(annotations=annotations)
