# ADR 0001: Compute and Cache Indicator in the Data Service

## Status

Accepted for MVP.

## Decision

Steady N Wise computes the supply oscillator in the Python data service with polars, exposes the result through FastAPI, caches gateway responses in Redis, and renders the chart in React with ECharts.

## Context

The oscillator must remain auditable against the Excel-derived formula:

```text
supply_ratio = (foreign_net + institution_net) / market_cap
macd = EMA12(supply_ratio) - EMA26(supply_ratio)
signal = EMA9(macd)
oscillator = macd - signal
```

EMA parameters are fixed as `span=12`, `span=26`, `span=9`, and `adjust=False`.

## Consequences

- Python owns financial calculation correctness and fixture regression tests.
- Bun/Elysia stays focused on request validation, caching, fallback, and frontend-facing contracts.
- React renders only validated API data and does not recompute the finance formula.
- Range-keyed Redis cache is simple for MVP; per-day chunks and cache pre-warming are post-MVP.
