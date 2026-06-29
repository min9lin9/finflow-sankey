# Steady N Wise Design System

## 1. Atmosphere & Identity

Steady N Wise is a quiet finance command center: dense enough for repeated market analysis, calm enough to read under pressure. The signature is restrained tabular precision, with a fixed shell, muted surfaces, and blue used only for active financial actions and focus.

## 2. Color

### Palette

| Role | Token | Light | Dark | Usage |
|------|-------|-------|------|-------|
| Surface/primary | --surface-primary | #FFFFFF | #111111 | Main canvas |
| Surface/secondary | --surface-secondary | #F7F8FA | #17191C | App sidebars and chart background |
| Surface/elevated | --surface-elevated | #FFFFFF | #20242A | Dropdowns, popovers, panels |
| Text/primary | --text-primary | #191F28 | #F7F8FA | Headlines, primary body |
| Text/secondary | --text-secondary | #6B7684 | #B0B8C1 | Secondary copy |
| Text/tertiary | --text-tertiary | #8B95A1 | #7E8792 | Metadata and disabled text |
| Border/default | --border-default | #E5E8EB | #30343A | Dividers and outlines |
| Border/subtle | --border-subtle | #F2F4F6 | #24272D | Soft panel separation |
| Accent/primary | --accent-primary | #3182F6 | #64A8FF | Primary action, active chart line, focus |
| Accent/hover | --accent-hover | #1B64DA | #8BC0FF | Hover action |
| Chart/market-cap | --chart-market-cap | #3182F6 | #64A8FF | Market-cap series |
| Chart/oscillator | --chart-oscillator | #03B26C | #41D092 | Oscillator series |
| Status/success | --status-success | #03B26C | #41D092 | Positive states |
| Status/warning | --status-warning | #F59F00 | #FFBC42 | Warnings |
| Status/error | --status-error | #F04452 | #FF6B78 | Errors |
| Status/info | --status-info | #3182F6 | #64A8FF | Informational states |

### Rules

- Accent colors are semantic only: interaction, focus, and chart data.
- Large background areas stay neutral; no gradients or decorative color fields.
- New colors must be added here before use.

## 3. Typography

### Scale

| Level | Size | Weight | Line Height | Tracking | Usage |
|-------|------|--------|-------------|----------|-------|
| Display | 40px | 700 | 1.15 | 0 | Page title |
| H1 | 32px | 700 | 1.2 | 0 | View headers |
| H2 | 24px | 700 | 1.3 | 0 | Panel headers |
| H3 | 18px | 700 | 1.4 | 0 | Card titles |
| Body/lg | 17px | 500 | 1.6 | 0 | Lead text |
| Body | 15px | 400 | 1.6 | 0 | Default UI text |
| Body/sm | 13px | 400 | 1.5 | 0 | Secondary info |
| Caption | 12px | 600 | 1.4 | 0 | Labels, metadata |
| Overline | 11px | 700 | 1.3 | 0.08em | Section labels |

### Font Stack

- Primary: Pretendard, SF Pro Display, Apple SD Gothic Neo, Noto Sans KR, system-ui, sans-serif
- Mono: SF Mono, JetBrains Mono, ui-monospace, monospace

### Rules

- Financial values use `font-variant-numeric: tabular-nums`.
- Body text is never below 13px in the app shell.
- Letter spacing is 0 except overline labels.

## 4. Spacing & Layout

### Base Unit

All spacing derives from a base of 4px.

| Token | Value | Usage |
|-------|-------|-------|
| --space-1 | 4px | Tight inline spacing |
| --space-2 | 8px | Compact groups |
| --space-3 | 12px | Field padding |
| --space-4 | 16px | Default panel padding |
| --space-5 | 20px | Comfortable grouping |
| --space-6 | 24px | Main card padding |
| --space-8 | 32px | Section separation |
| --space-10 | 40px | Major inner spacing |
| --space-12 | 48px | View separation |
| --space-16 | 64px | Page-level rhythm |

### Grid

- Max content width: 1440px
- App shell: fixed topbar, left rail, main chart workspace, optional right panel
- Breakpoints: sm 640px, md 768px, lg 1024px, xl 1280px

### Rules

- No nested cards. Panels sit directly in the app workspace.
- Repeated fixed-format controls use stable dimensions to avoid layout shift.

## 5. Components

### TopBar
- Structure: header with product mark, stock search, health indicator.
- States: search default, focus, loading, empty, error.
- Accessibility: search input has a label and keyboard-selectable listbox.

### SupplyChartPanel
- Structure: header, period segmented control, ECharts canvas region, chart state.
- States: loading, ready, error, empty.
- Accessibility: chart has textual summary and period buttons are real buttons.

### SidePanel
- Structure: compact metrics list and system notes.
- States: expanded on desktop, stacked on mobile.
- Accessibility: landmarks and headings identify regions.

## 6. Motion & Interaction

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 120ms | ease-out | Button press, focus |
| Standard | 220ms | ease-in-out | Dropdown and panel state |
| Emphasis | 420ms | cubic-bezier(0.16, 1, 0.3, 1) | Initial chart reveal |

### Rules

- Animate only transform and opacity.
- Respect `prefers-reduced-motion`.
- Every interactive control has hover, active, and focus-visible states.

## 7. Depth & Surface

### Strategy

Borders-only with tonal shifts. Use `1px solid var(--border-default)` for panels and `var(--surface-secondary)` for the workspace. Shadows are reserved for dropdowns only and must stay below `rgba(0,0,0,0.08)`.
