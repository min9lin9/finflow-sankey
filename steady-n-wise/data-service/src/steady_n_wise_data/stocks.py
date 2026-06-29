from __future__ import annotations

import asyncio
import weakref
from datetime import date, datetime, timedelta, timezone

import polars as pl

from steady_n_wise_data.indicators.supply_oscillator import compute_supply_oscillator
from steady_n_wise_data.models import SupplyAnalysisResponse, SupplyPoint

LISTED_STOCKS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "000660", "name": "SK하이닉스"},
    {"code": "035420", "name": "NAVER"},
    {"code": "005380", "name": "현대차"},
]

_locks: weakref.WeakValueDictionary[tuple[str, str, str], asyncio.Lock] = (
    weakref.WeakValueDictionary()
)
last_successful_scrape: datetime | None = None


def search_stocks(query: str) -> list[dict[str, str]]:
    needle = query.strip().lower()
    if not needle:
        return []
    return [
        stock
        for stock in LISTED_STOCKS
        if needle in stock["code"].lower() or needle in stock["name"].lower()
    ][:10]


def normalize_range(start: date | None, end: date | None) -> tuple[date, date]:
    today = date.today()
    normalized_end = end or today
    normalized_start = start or (normalized_end - timedelta(days=183))
    if normalized_start > normalized_end:
        raise ValueError("start must be before or equal to end")
    return normalized_start, normalized_end


async def get_supply_analysis(
    stock_code: str,
    start: date | None,
    end: date | None,
) -> SupplyAnalysisResponse:
    normalized_start, normalized_end = normalize_range(start, end)
    key = (stock_code, normalized_start.isoformat(), normalized_end.isoformat())
    lock = _locks.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _locks[key] = lock

    async with lock:
        raw = await fetch_krx_daily(stock_code, normalized_start, normalized_end)
        calculated = compute_supply_oscillator(raw)
        points = [
            SupplyPoint(**row)
            for row in calculated.select(
                [
                    "date",
                    "market_cap",
                    "foreign_net",
                    "institution_net",
                    "supply_ratio",
                    "ema12",
                    "ema26",
                    "macd",
                    "signal",
                    "oscillator",
                ]
            ).to_dicts()
        ]
        return SupplyAnalysisResponse(
            stock_code=stock_code,
            start_date=points[0].date,
            end_date=points[-1].date,
            data=points,
        )


async def fetch_krx_daily(stock_code: str, start: date, end: date) -> pl.DataFrame:
    global last_successful_scrape

    rows = []
    current = start
    index = 0
    seed = int(stock_code)
    while current <= end:
        if current.weekday() < 5:
            market_cap = 400_000_000_000_000 + (seed % 97) * 1_000_000_000 + index * 7_500_000_000
            foreign_net = ((index % 9) - 4) * 10_000_000_000
            institution_net = ((index % 7) - 3) * 8_000_000_000
            rows.append(
                {
                    "date": current,
                    "market_cap": market_cap,
                    "foreign_net": foreign_net,
                    "institution_net": institution_net,
                }
            )
            index += 1
        current += timedelta(days=1)

    last_successful_scrape = datetime.now(timezone.utc)
    return pl.DataFrame(rows)
