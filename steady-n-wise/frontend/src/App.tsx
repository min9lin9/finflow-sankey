import { useEffect, useMemo, useState } from "react";

import type { StockSearchResult, SupplyResponse } from "./api";
import { fetchSupplyAnalysis } from "./api";
import { type Period, toDateRange } from "./dateRange";
import { StockSearch } from "./StockSearch";
import { SupplyChart } from "./SupplyChart";

const defaultStock = { code: "005930", name: "삼성전자" };
const periods: Period[] = ["1M", "3M", "6M", "1Y", "ALL"];

export function App() {
  const [stock, setStock] = useState<StockSearchResult>(defaultStock);
  const [period, setPeriod] = useState<Period>("6M");
  const [response, setResponse] = useState<SupplyResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const range = useMemo(() => toDateRange(period), [period]);

  useEffect(() => {
    setStatus("loading");
    fetchSupplyAnalysis(stock.code, range)
      .then((data) => {
        setResponse(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, [stock, range]);

  const latest = response?.data.at(-1);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand__mark">SNW</span>
          <span className="brand__name">Steady N Wise</span>
        </div>
        <StockSearch selected={stock} onSelect={setStock} />
        <div className="health">Local MVP</div>
      </header>

      <aside className="left-rail" aria-label="주요 메뉴">
        <button className="rail-button rail-button--active" type="button">시장</button>
        <button className="rail-button" type="button">공시</button>
        <button className="rail-button" type="button">리서치</button>
      </aside>

      <main className="workspace">
        <section className="chart-panel" aria-labelledby="chart-title">
          <div className="panel-head">
            <div>
              <p className="overline">SUPPLY ANALYSIS</p>
              <h1 id="chart-title">{stock.name} 수급 대시보드</h1>
              <p className="summary">
                시가총액과 외국인·기관 순매수 기반 오실레이터를 같은 시간축에서 비교합니다.
              </p>
            </div>
            <div className="periods" aria-label="조회 기간">
              {periods.map((item) => (
                <button
                  className={item === period ? "period period--active" : "period"}
                  key={item}
                  type="button"
                  onClick={() => setPeriod(item)}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {status === "loading" && <div className="state">차트 데이터를 불러오는 중</div>}
          {status === "error" && <div className="state state--error">차트 데이터를 불러오지 못했습니다.</div>}
          {status === "ready" && <SupplyChart response={response} />}
        </section>
      </main>

      <aside className="right-panel" aria-label="요약 지표">
        <p className="overline">CURRENT</p>
        <h2>{stock.code}</h2>
        <dl className="metrics">
          <div>
            <dt>최근 거래일</dt>
            <dd>{latest?.date ?? "-"}</dd>
          </div>
          <div>
            <dt>시가총액</dt>
            <dd>{latest ? `${Math.round(latest.market_cap / 1_000_000_000_000)}조` : "-"}</dd>
          </div>
          <div>
            <dt>오실레이터</dt>
            <dd>{latest ? latest.oscillator.toExponential(2) : "-"}</dd>
          </div>
        </dl>
      </aside>
    </div>
  );
}
