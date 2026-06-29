from __future__ import annotations

from fastapi.testclient import TestClient

from steady_n_wise_data.app import app


client = TestClient(app)


def test_search_returns_samsung() -> None:
    response = client.get("/stocks/search?q=삼성")

    assert response.status_code == 200
    assert {"code": "005930", "name": "삼성전자"} in response.json()


def test_supply_analysis_contract() -> None:
    response = client.get("/stocks/005930/supply-analysis?start=2026-01-02&end=2026-01-16")

    assert response.status_code == 200
    body = response.json()
    assert body["stock_code"] == "005930"
    assert body["data"]
    assert {"market_cap", "oscillator", "macd", "signal"}.issubset(body["data"][0])


def test_supply_analysis_rejects_bad_code() -> None:
    response = client.get("/stocks/ABC/supply-analysis")

    assert response.status_code == 422
