"""Sankey pipeline orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
from plotly.graph_objects import Figure

from finflow_sankey.core.graph import FinancialGraph
from finflow_sankey.core.mapper import AccountMapper
from finflow_sankey.core.normalizer import SignNormalizer, UnitNormalizer
from finflow_sankey.core.palette import ColorPalette, get_palette
from finflow_sankey.core.schema import InputSchema
from finflow_sankey.core.validator import FinancialValidator
from finflow_sankey.renderers.base import Renderer
from finflow_sankey.renderers.plotly_renderer import PlotlyRenderer
from finflow_sankey.templates.base import StatementTemplate


class SankeyPipeline:
    """Pipeline for building and rendering financial Sankey diagrams."""

    def __init__(
        self,
        data: pl.DataFrame | pl.LazyFrame,
        template: StatementTemplate,
        period: str | None = None,
        currency: str | None = None,
        default_palette: ColorPalette | None = None,
        mapping: AccountMapper | dict | str | Path | None = None,
        layout: str | None = None,
    ):
        self._lf = self._to_lazy_frame(data)
        self.template = template
        self.period = period
        self.currency = currency
        self.default_palette = default_palette
        self.layout = layout
        self._mapper = self._resolve_mapper(mapping)
        self._validated_df: pl.DataFrame | None = None
        self._graph: FinancialGraph | None = None
        self._sign_normalizer = SignNormalizer(expense_sign="positive")
        self._unit_normalizer = UnitNormalizer()

    def _to_lazy_frame(self, data: pl.DataFrame | pl.LazyFrame) -> pl.LazyFrame:
        """Convert input data to Polars LazyFrame."""
        if isinstance(data, pl.LazyFrame):
            return data
        if isinstance(data, pl.DataFrame):
            return data.lazy()

        raise TypeError(
            "Input data must be a Polars DataFrame or Polars LazyFrame."
        )

    def _resolve_mapper(
        self, mapping: AccountMapper | dict | str | Path | None
    ) -> AccountMapper | None:
        if mapping is None:
            return None
        if isinstance(mapping, AccountMapper):
            return mapping
        if isinstance(mapping, dict):
            return AccountMapper.from_dict(mapping)
        return AccountMapper.from_yaml(mapping)

    def validate(self, tolerance: float = 0.01) -> "SankeyPipeline":
        """Validate input data."""
        df = self._prepare_df()
        validator = FinancialValidator(self.template.statement_type)
        self._validated_df = validator.validate(
            df,
            required_roles=self.template.required_roles(),
            tolerance=tolerance,
        )
        return self

    def normalize_signs(self) -> "SankeyPipeline":
        """Normalize signs (already done in _prepare_df by default)."""
        return self

    def group_minor(
        self,
        min_pct: float | None = None,
        min_value: float | None = None,
        top_n: int | None = None,
        label: str = "Other",
    ) -> "SankeyPipeline":
        """Group minor accounts into Other.

        Args:
            min_pct: Group accounts below this percentage of total sankey_value.
            min_value: Group accounts below this absolute sankey_value.
            top_n: Keep top_n accounts, group the rest.
            label: Label for the grouped accounts.
        """
        if self._validated_df is None:
            raise RuntimeError("Must call validate() before group_minor().")

        df = self._validated_df

        if min_pct is not None and min_value is not None:
            total = df["sankey_value"].sum()
            threshold = max(total * min_pct, min_value)
            df = self._group_by_threshold(df, threshold, label)
        elif min_pct is not None:
            total = df["sankey_value"].sum()
            df = self._group_by_threshold(df, total * min_pct, label)
        elif min_value is not None:
            df = self._group_by_threshold(df, min_value, label)
        elif top_n is not None:
            df = self._group_by_top_n(df, top_n, label)

        self._validated_df = df
        return self

    def _group_by_threshold(
        self, df: pl.DataFrame, threshold: float, label: str
    ) -> pl.DataFrame:
        threshold = max(threshold, 0.0)

        df = df.with_columns(
            pl.when(pl.col("sankey_value") < threshold)
            .then(pl.lit(label))
            .otherwise(pl.col("account"))
            .alias("account_group")
        )

        grouped = df.group_by(["account_group", "section"]).agg(
            pl.col("value").sum().alias("value"),
            pl.col("sankey_value").sum().alias("sankey_value"),
            pl.col("display_value").sum().alias("display_value"),
            pl.col("period").first().alias("period"),
            pl.col("currency").first().alias("currency"),
            pl.col("statement").first().alias("statement"),
            pl.col("account").alias("original_accounts"),
        )

        grouped = self._finalize_group_label(grouped, label)
        return grouped

    def _group_by_top_n(self, df: pl.DataFrame, top_n: int, label: str) -> pl.DataFrame:
        if top_n <= 0:
            raise ValueError("top_n must be a positive integer.")

        sorted_df = df.sort("sankey_value", descending=True)
        top_accounts = sorted_df.head(top_n)["account"].to_list()

        df = df.with_columns(
            pl.when(pl.col("account").is_in(top_accounts))
            .then(pl.col("account"))
            .otherwise(pl.lit(label))
            .alias("account_group")
        )

        grouped = df.group_by(["account_group", "section"]).agg(
            pl.col("value").sum().alias("value"),
            pl.col("sankey_value").sum().alias("sankey_value"),
            pl.col("display_value").sum().alias("display_value"),
            pl.col("period").first().alias("period"),
            pl.col("currency").first().alias("currency"),
            pl.col("statement").first().alias("statement"),
            pl.col("account").alias("original_accounts"),
        )

        grouped = self._finalize_group_label(grouped, label)
        return grouped

    def _finalize_group_label(self, grouped: pl.DataFrame, label: str) -> pl.DataFrame:
        """Add is_grouped flag and set account label with count for grouped rows."""
        grouped = grouped.with_columns(
            pl.when(pl.col("account_group") == label)
            .then(True)
            .otherwise(False)
            .alias("is_grouped"),
        )

        grouped = grouped.with_columns(
            pl.when(pl.col("is_grouped"))
            .then(
                pl.lit(f"{label} (")
                + pl.col("original_accounts").list.len().cast(pl.Utf8)
                + pl.lit(" accounts)")
            )
            .otherwise(pl.col("account_group"))
            .alias("account")
        )
        return grouped

    def with_palette(
        self,
        palette: str | Path | dict[str, Any] | ColorPalette | None = None,
    ) -> "SankeyPipeline":
        """Set default palette for rendering."""
        self.default_palette = get_palette(palette)
        return self

    def render(
        self,
        title: str | None = None,
        renderer: str = "plotly",
        palette: str | Path | dict[str, Any] | ColorPalette | None = None,
        theme: str | None = None,
    ) -> Figure:
        """Render the Sankey graph."""
        if self._validated_df is None:
            self.validate()

        graph = self.template.build(self._validated_df, layout=self.layout)

        resolved_palette = self._resolve_palette(palette, theme)

        renderer_obj = self._get_renderer(renderer)
        return renderer_obj.render(graph, resolved_palette, title=title)

    def export_html(
        self,
        path: str | Path,
        title: str | None = None,
        renderer: str = "plotly",
        palette: str | Path | dict[str, Any] | ColorPalette | None = None,
        theme: str | None = None,
        **render_kwargs,
    ) -> str:
        """Render and export the Sankey graph to HTML.

        Args:
            path: Output HTML file path.
            title: Chart title.
            renderer: Renderer name (default: "plotly").
            palette: Custom palette override.
            theme: Built-in theme name.
            **render_kwargs: Additional kwargs passed to render().

        Returns:
            The output file path as a string.
        """
        fig = self.render(
            title=title,
            renderer=renderer,
            palette=palette,
            theme=theme,
            **render_kwargs,
        )
        fig.write_html(str(path))
        return str(path)

    def _resolve_palette(
        self,
        palette: str | Path | dict[str, Any] | ColorPalette | None,
        theme: str | None,
    ) -> ColorPalette:
        """Resolve palette with priority: palette arg > theme > default_palette > built-in."""
        if palette is not None:
            pal = get_palette(palette, theme=theme)
            return pal

        if theme is not None:
            return get_palette(theme=theme)

        if self.default_palette is not None:
            return self.default_palette

        return get_palette()

    def _get_renderer(self, renderer: str) -> Renderer:
        if renderer == "plotly":
            return PlotlyRenderer()
        raise ValueError(f"Unknown renderer: {renderer}")

    def _prepare_df(self) -> pl.DataFrame:
        """Prepare data: schema validation, normalization, sign normalization, mapping."""
        schema = InputSchema(self._lf)
        lf = schema.validate().normalize()
        lf = self._sign_normalizer.normalize(lf)
        lf = self._unit_normalizer.normalize(lf)

        df = lf.collect()

        if self.period:
            df = df.with_columns(pl.lit(self.period).alias("period"))
        if self.currency:
            df = df.with_columns(pl.lit(self.currency).alias("currency"))
        if self._mapper is not None:
            df = self._mapper.apply(df)

        return df

    @property
    def graph(self) -> FinancialGraph:
        if self._graph is None:
            if self._validated_df is None:
                self.validate()
            self._graph = self.template.build(self._validated_df, layout=self.layout)
        return self._graph
