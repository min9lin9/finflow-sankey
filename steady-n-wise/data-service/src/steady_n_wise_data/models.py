from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class StockSearchResult(BaseModel):
    code: str = Field(pattern=r"^\d{6}$")
    name: str


class SupplyPoint(BaseModel):
    date: date
    market_cap: int
    foreign_net: int
    institution_net: int
    supply_ratio: float
    ema12: float
    ema26: float
    macd: float
    signal: float
    oscillator: float


class SupplyAnalysisResponse(BaseModel):
    stock_code: str = Field(pattern=r"^\d{6}$")
    start_date: date
    end_date: date
    data: list[SupplyPoint]

    @field_validator("data")
    @classmethod
    def require_rows(cls, rows: list[SupplyPoint]) -> list[SupplyPoint]:
        if not rows:
            raise ValueError("supply analysis requires at least one row")
        return rows


class HealthResponse(BaseModel):
    status: str
    redis: str
    last_successful_scrape: datetime | None
    timestamp: datetime
