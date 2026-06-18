from __future__ import annotations

import plotly.graph_objects as go

from finflow_sankey.core.graph import FinancialGraph
from finflow_sankey.core.palette import ColorPalette


def apply_reference_layout(
    fig: go.Figure,
    palette: ColorPalette,
    title_text: str,
    graph: FinancialGraph,
) -> None:
    node_count = max(len(graph.nodes), 1)
    total_revenue = graph.get_role_amount("revenue") or 1.0
    max_link = max((link.amount for link in graph.links), default=0.0)
    max_ratio = max_link / total_revenue
    height = max(720, 540 + node_count * 34 + int(max_ratio * 180))

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
        margin=dict(l=40, r=40, t=90, b=40),
        showlegend=False,
        height=height,
        width=1100,
    )


def add_reference_legend(fig: go.Figure, palette: ColorPalette) -> None:
    items = (
        ("Revenue", palette.roles.revenue),
        ("Profit", palette.roles.profit),
        ("Expense", palette.roles.operating_expenses),
    )
    annotations = [
        dict(
            x=0.02,
            y=1.02 - index * 0.045,
            xref="paper",
            yref="paper",
            text=f"<span style='color:{color};'>■</span> {label}",
            showarrow=False,
            font=dict(
                size=12,
                color=palette.semantic.text,
                family=palette.semantic.font_family,
            ),
            align="left",
        )
        for index, (label, color) in enumerate(items)
    ]
    fig.update_layout(annotations=annotations)
