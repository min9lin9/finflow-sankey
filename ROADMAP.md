# FinFlow Sankey Roadmap

> Last updated: 2026-06-13

## Versioning Policy

FinFlow Sankey follows [Semantic Versioning](https://semver.org/lang/ko/).

- `0.1.x`: Active development. New features and minor breaking changes may occur.
- `0.2.x`: Stabilization. Focus on API consistency, documentation, and data-source adapters.
- `1.0.0`: Stable release. Backward compatibility guaranteed within major version.

---

## 0.1.x (Current) — Feature Foundation

**Goal**: Make core Sankey visualization work for income statement, cash flow, and balance sheet.

- [x] Income statement Sankey with intermediate nodes
- [x] Cash flow statement bridge
- [x] Balance sheet reconciliation view
- [x] Multi-period comparison
- [x] Color palette system (YAML + runtime override)
- [x] Account mapping (YAML + dict)
- [x] Reference layout (`layout="reference"`) for income statement
- [x] Polars-first input (no pandas required)
- [x] HTML export
- [x] GitHub Actions CI + PyPI trusted publishing
- [x] GitHub Pages documentation

---

## 0.2.x — Stabilization & Documentation

**Goal**: Lower the barrier for external users and stabilize the public API.

### 0.2.0 — Documentation & Examples

- [ ] Restructure README with quickstart, API summary, and FAQ
- [ ] Auto-generated API reference (`mkdocstrings`)
- [ ] Jupyter notebook examples
- [ ] CSV/Excel input examples
- [ ] DART OpenAPI (`dart-fss`) integration example
- [ ] `license = "MIT"` SPDX migration in `pyproject.toml`

### 0.2.1 — Data Adapters

- [x] `load_*_csv()` helpers for simple CSV files
- [x] `load_*_excel()` helpers for Excel workbooks
- [x] `DartlabAdapter` class wrapping Dartlab CLI
- [x] `DartFssAdapter` class wrapping `dart-fss`

### 0.2.2 — API Consistency

- [x] Review `layout` parameter across all statement types
- [x] Consistent `group_minor()` behavior for reference layout
- [x] Standardize error messages and validation hints

---

## 0.3.x — Quality & Edge Cases

**Goal**: Reach production confidence through edge-case handling and performance.

- [x] Edge case test suite (zero values, missing sections, negative values, extreme ratios)
- [x] Rendering performance benchmarks
- [x] Grouping and aggregation helpers for large account lists
- [x] Better label collision handling for reference layout

---

## 1.0.0 — Stable Release

**Goal**: Declare stable public API.

- [ ] Freeze public API for `FinancialSankey`, `SankeyPipeline`, and `ColorPalette`
- [ ] Complete API documentation and migration guide
- [ ] Community guidelines: `CONTRIBUTING.md`, Code of Conduct
- [ ] Issue/PR templates
- [ ] At least 3 external users/projects confirmed using the library

---

## Post-1.0 Ideas

- Interactive web dashboard template
- PDF export support
- Internationalization (i18n) for labels and legends
- Additional chart types (waterfall, treemap)
- Plugin system for custom templates

---

## Breaking Changes Policy

Until `1.0.0`, breaking changes may occur in `0.x` releases. We will:

1. Document them in `CHANGELOG.md` under a "Breaking Changes" section.
2. Provide migration notes in the release notes.
3. Avoid breaking changes within `0.2.x` patch releases once `0.2.0` is published.
