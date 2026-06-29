import { useEffect, useId, useState } from "react";

import type { StockSearchResult } from "./api";
import { searchStocks } from "./api";

interface StockSearchProps {
  selected: StockSearchResult;
  onSelect: (stock: StockSearchResult) => void;
}

export function StockSearch({ selected, onSelect }: StockSearchProps) {
  const listboxId = useId();
  const [query, setQuery] = useState(selected.name);
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [hasUserInput, setHasUserInput] = useState(false);

  useEffect(() => {
    if (!hasUserInput || query.trim().length < 1) {
      setResults([]);
      return;
    }
    const timer = window.setTimeout(() => {
      setStatus("loading");
      searchStocks(query)
        .then((items) => {
          setResults(items);
          setStatus("idle");
        })
        .catch(() => setStatus("error"));
    }, 180);
    return () => window.clearTimeout(timer);
  }, [hasUserInput, query]);

  return (
    <div className="search">
      <label className="search__label" htmlFor="stock-search">
        종목 검색
      </label>
      <input
        id="stock-search"
        className="search__input"
        value={query}
        placeholder="삼성전자 또는 005930"
        role="combobox"
        aria-controls={listboxId}
        aria-expanded={results.length > 0}
        onChange={(event) => {
          setHasUserInput(true);
          setQuery(event.target.value);
        }}
      />
      {results.length > 0 && (
        <div className="search__list" id={listboxId} role="listbox">
          {results.map((stock) => (
            <button
              className="search__option"
              key={stock.code}
              type="button"
              role="option"
                onClick={() => {
                  onSelect(stock);
                  setQuery(stock.name);
                  setHasUserInput(false);
                  setResults([]);
                }}
            >
              <span>{stock.name}</span>
              <span className="search__code">{stock.code}</span>
            </button>
          ))}
        </div>
      )}
      {status === "loading" && <span className="search__status">검색 중</span>}
      {status === "error" && <span className="search__status search__status--error">검색 실패</span>}
    </div>
  );
}
