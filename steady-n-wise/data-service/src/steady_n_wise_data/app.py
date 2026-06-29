from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException, Query

from steady_n_wise_data import stocks
from steady_n_wise_data.models import HealthResponse, StockSearchResult, SupplyAnalysisResponse

app = FastAPI(title="Steady N Wise Data Service", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        redis="not_configured",
        last_successful_scrape=stocks.last_successful_scrape,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/stocks/search", response_model=list[StockSearchResult])
async def search(q: str = Query(min_length=1, max_length=30)) -> list[StockSearchResult]:
    return [StockSearchResult(**row) for row in stocks.search_stocks(q)]


@app.get("/stocks/{stock_code}/supply-analysis", response_model=SupplyAnalysisResponse)
async def supply_analysis(
    stock_code: str,
    start: date | None = None,
    end: date | None = None,
) -> SupplyAnalysisResponse:
    if len(stock_code) != 6 or not stock_code.isdigit():
        raise HTTPException(status_code=422, detail="stock_code must be a 6 digit KRX code")
    try:
        return await stocks.get_supply_analysis(stock_code, start, end)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
