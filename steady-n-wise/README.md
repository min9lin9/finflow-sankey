# Steady N Wise

Finance OS dashboard MVP for Korean equities. The first slice lets a user search for a KRX stock and view market cap with the supply oscillator in an ECharts overlay.

## Local Development

```bash
cp .env.example .env
make compose-config
make dev
```

Stop the stack:

```bash
make down
```

## Test Commands

```bash
make test-data
make test-backend
make test-frontend
make test-e2e
```

## Architecture

- `data-service`: FastAPI, polars, PyKRX adapter boundary, oscillator calculation.
- `backend`: Bun and Elysia API gateway, Redis cache, retry/fallback, single-flight.
- `frontend`: React, Vite, ECharts, Pretendard/TDS-inspired dashboard UI.
- `redis`: daily cache for `supply:{code}:{start}:{end}`.

The oscillator formula is:

```text
supply_ratio = (foreign_net + institution_net) / market_cap
macd = EMA12(supply_ratio) - EMA26(supply_ratio)
signal = EMA9(macd)
oscillator = macd - signal
```

EMA uses `span=12/26/9` and `adjust=False`.

## MVP Exclusions

This MVP does not implement OpenDART/dartlab screens, auth, settings UI, real-time intraday data, Redis pre-warming, or per-day Redis chunks.
