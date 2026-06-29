# Data Service

FastAPI service for KRX search, raw market data access, and supply oscillator calculation.

## Formula

```text
supply_ratio = (foreign_net + institution_net) / market_cap
ema12 = ewm_mean(supply_ratio, span=12, adjust=False)
ema26 = ewm_mean(supply_ratio, span=26, adjust=False)
macd = ema12 - ema26
signal = ewm_mean(macd, span=9, adjust=False)
oscillator = macd - signal
```

## Fixture Recipe

- Ticker: `005930` (삼성전자)
- Date range: `2025-06-02` to `2026-05-29`
- CSV header: `date,market_cap,foreign_net,institution_net,supply_ratio,ema12,ema26,macd,signal,oscillator`
- Unit tests compare calculated values within `1e-12`.
