# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-14

### Added
- `finflow_sankey.adapters` package:
  - `load_income_statement_csv`, `load_cash_flow_csv`, `load_balance_sheet_csv`
  - `load_income_statement_excel`, `load_cash_flow_excel`, `load_balance_sheet_excel`
  - `DartlabAdapter` for Dartlab CLI data
  - `DartFssAdapter` for DART OpenAPI (`dart-fss`)
- `docs/adapters.md` guide.
- `tests/test_adapters.py` (6 tests).

## [0.1.16] - 2026-06-14

### Added
- GitHub Issue templates (bug report, feature request, question).
- Pull request template.
- `CONTRIBUTING.md` development guide.
- Edge case test suite (`tests/test_edge_cases.py`).
- GitHub Discussions enabled.

## [0.1.15] - 2026-06-14

### Added
- CSV input example (`examples/from_csv.py`).
- Excel input example (`examples/from_excel.py`).
- DART OpenAPI (`dart-fss`) integration example (`examples/dart_fss_integration.py`).
- Jupyter notebooks: `01_income_statement.ipynb`, `02_reference_layout.ipynb`.
- `docs/mapping.md` account mapping guide.
- `docs/faq.md` frequently asked questions.

## [0.1.14] - 2026-06-13

### Added
- `ROADMAP.md` with v0.2.x to v1.0 release plan.
- Auto-generated API reference using `mkdocstrings`.
- PyPI badges and improved README structure.

### Changed
- Restructured `README.md` for first-time users (input format, sections, examples).
- Migrated `pyproject.toml` license to SPDX format (`license = "MIT"`).
- Updated project URLs to `min9lin9/finflow-sankey`.

## [0.1.13] - 2026-06-13

### Added
- Opt-in `layout="reference"` for income statement with detailed account nodes.
- Reference layout uses fixed Plotly arrangement, auto height, and grouped legend.
- Palette-based reference colors and borders (no hardcoded theme exceptions).

### Changed
- `StatementTemplate.build()` accepts `**kwargs` for layout forwarding.
- Default palette uses reference-inspired role colors and `node_border_width: 0`.

## [0.1.12] - 2026-06-13

### Added
- Value labels on every Sankey node (compact T/B/M/K formatting).
- Non-operating income support in income statement template.

### Changed
- Income statement template now skips unnecessary intermediate nodes when COGS or OpEx data is missing.
- Validator handles non-operating income in profit reconciliation.
- Improved Dartlab integration example derives operating expenses and tax benefit.

## [0.1.11] - 2026-06-13

### Changed
- Redesigned income statement Sankey with intermediate nodes (Gross Profit, Operating Income).
- Links are now colored by target role for clearer expense/profit flow.
- Added explicit vertical node positioning across all templates.
- Improved default palette colors, link opacity, and typography.
- Fixed sign normalization for `cost_of_revenue` and `operating_expenses` sections.

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
