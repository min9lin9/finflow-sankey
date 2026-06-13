# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2026-06-12

### Added
- Multi-period comparison Sankey (`FinancialSankey.multi_period_compare`).
- Support for comparing exactly two periods side-by-side.

### Changed
- Validator skips single-period and duplicate-account checks for multi-period comparison.

## [0.1.9] - 2026-06-12

### Added
- Dark mode theme (`theme="dark"`).

## [0.1.8] - 2026-06-12

### Added
- Optional pandas adapter (`pip install finflow-sankey[pandas]`).

## [0.1.7] - 2026-06-12

### Added
- YAML account mapping support (`mapping="path/to/mapping.yaml"`).
- Runtime dict mapping support (`mapping={"revenue": ["Net Sales"], ...}`).
- Default mapping files for income statement, cash flow, and balance sheet.

## [0.1.6] - 2026-06-12

### Added
- Balance sheet reconciliation Sankey.
- Left/right split layout for assets vs liabilities and equity.
- `[Reconciliation View]` title prefix.

## [0.1.5] - 2026-06-12

### Added
- Level-based horizontal node positioning.
- Support for explicit node `x` coordinates in templates.

## [0.1.4] - 2026-06-12

### Added
- Comprehensive edge-case tests for validation errors.

## [0.1.3] - 2026-06-12

### Added
- Rich hover metadata: original accounts, period, currency, role, validation status.

## [0.1.2] - 2026-06-12

### Added
- Minor grouping enhancement (`group_minor`).
- Support for `top_n`, `min_pct`, and `min_value` grouping strategies.
- Grouped account count in "Other (n accounts)" label.

## [0.1.1] - 2026-06-12

### Added
- HTML export helper (`pipeline.export_html()`).

## [0.1.0] - 2026-06-12

### Added
- Initial MVP release.
- Polars-first pipeline (`DataFrame` and `LazyFrame` support).
- Income statement Sankey template.
- Cash flow statement Sankey template.
- Plotly renderer with role-based color palettes.
- Built-in themes: default, monochrome, colorblind_safe, minimal.
- Runtime palette override via dict or YAML.
- Accounting validation (period, currency, reconciliation, missing accounts).
