"""Color palette system for FinFlow Sankey."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .exceptions import InvalidColorError, InvalidOpacityError, MissingRoleColorError


REQUIRED_ROLES = {"revenue", "operating_expenses", "profit", "other"}
ALL_ROLES = {
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "non_operating_items",
    "tax",
    "profit",
    "net_income",
    "cash_inflow",
    "cash_outflow",
    "cash_balance",
    "asset",
    "liability",
    "equity",
    "other",
}


def _is_valid_hex(color: str) -> bool:
    """Validate hex color format."""
    if not isinstance(color, str):
        return False
    return bool(re.fullmatch(r"^#([0-9A-Fa-f]{3}){1,2}$", color))


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


@dataclass(frozen=True)
class RolePalette:
    """Color definitions for each financial role."""

    revenue: str = "#2563EB"
    cost_of_revenue: str = "#F59E0B"
    operating_expenses: str = "#DC2626"
    non_operating_items: str = "#64748B"
    tax: str = "#7C3AED"
    profit: str = "#059669"
    net_income: str = "#059669"
    cash_inflow: str = "#0891B2"
    cash_outflow: str = "#E11D48"
    cash_balance: str = "#D97706"
    asset: str = "#1E3A8A"
    liability: str = "#9F1239"
    equity: str = "#15803D"
    other: str = "#94A3B8"


@dataclass(frozen=True)
class SemanticStyle:
    """Non-role visual styling."""

    background: str = "#FFFFFF"
    plot_background: str = "#F8FAFC"
    text: str = "#334155"
    border: str = "#334155"
    link_opacity: float = 0.45
    hover_opacity: float = 0.85
    node_border_width: float = 1.5
    link_border_width: float = 0.5
    node_thickness: int = 24
    font_family: str = "Inter, Pretendard, Arial"
    font_size: int = 12
    title_font_size: int = 18


@dataclass
class ColorPalette:
    """Complete color palette for rendering."""

    name: str = "default"
    version: str = "1.0.0"
    description: str = ""
    roles: RolePalette = field(default_factory=RolePalette)
    semantic: SemanticStyle = field(default_factory=SemanticStyle)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ColorPalette":
        """Load palette from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls._from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ColorPalette":
        """Load palette from dict."""
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "ColorPalette":
        roles_data = data.get("roles", {})
        semantic_data = data.get("semantic", {})

        return cls(
            name=data.get("name", "custom"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            roles=RolePalette(**roles_data),
            semantic=SemanticStyle(**semantic_data),
        )

    def override(self, overrides: dict[str, Any]) -> "ColorPalette":
        """Create a new palette with partial overrides."""
        role_fields = set(RolePalette.__dataclass_fields__.keys())
        semantic_fields = set(SemanticStyle.__dataclass_fields__.keys())

        role_overrides = {k: v for k, v in overrides.items() if k in role_fields}
        semantic_overrides = {k: v for k, v in overrides.items() if k in semantic_fields}

        return ColorPalette(
            name=f"{self.name}_overridden",
            version=self.version,
            description=self.description,
            roles=RolePalette(**{**self.roles.__dict__, **role_overrides}),
            semantic=SemanticStyle(**{**self.semantic.__dict__, **semantic_overrides}),
        )

    def validate(self) -> None:
        """Validate palette."""
        for role, color in self.roles.__dict__.items():
            if not _is_valid_hex(color):
                raise InvalidColorError(f"Invalid hex color for role '{role}': {color}")

        for semantic_key in ["background", "plot_background", "text", "border"]:
            color = getattr(self.semantic, semantic_key)
            if not _is_valid_hex(color):
                raise InvalidColorError(f"Invalid hex color for semantic '{semantic_key}': {color}")

        if not 0.0 <= self.semantic.link_opacity <= 1.0:
            raise InvalidOpacityError("link_opacity must be between 0 and 1")
        if not 0.0 <= self.semantic.hover_opacity <= 1.0:
            raise InvalidOpacityError("hover_opacity must be between 0 and 1")

        missing = REQUIRED_ROLES - set(self.roles.__dict__.keys())
        if missing:
            raise MissingRoleColorError(f"Missing required role colors: {missing}")

    def get_role_color(self, role: str) -> str:
        """Get color for a role, falling back to 'other'."""
        return getattr(self.roles, role, self.roles.other)


BUILT_IN_PALETTES: dict[str, ColorPalette] = {}


def _load_builtin_palettes() -> None:
    """Load built-in palettes from package directory."""
    package_dir = Path(__file__).parent.parent / "palettes"
    for theme in ["default", "monochrome", "colorblind_safe", "minimal", "dark"]:
        path = package_dir / f"{theme}.yaml"
        if path.exists():
            BUILT_IN_PALETTES[theme] = ColorPalette.from_yaml(path)


def get_palette(
    palette: str | Path | dict[str, Any] | ColorPalette | None = None,
    theme: str | None = None,
) -> ColorPalette:
    """Resolve palette from various inputs."""
    if isinstance(palette, ColorPalette):
        return palette

    if isinstance(palette, dict):
        base = BUILT_IN_PALETTES.get(theme, BUILT_IN_PALETTES["default"]) if theme else BUILT_IN_PALETTES["default"]
        return base.override(palette)

    if isinstance(palette, (str, Path)):
        pal = ColorPalette.from_yaml(palette)
        pal.validate()
        return pal

    if theme and theme in BUILT_IN_PALETTES:
        return BUILT_IN_PALETTES[theme]

    return BUILT_IN_PALETTES["default"]


_load_builtin_palettes()
