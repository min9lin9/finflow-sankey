"""DART OpenAPI adapter using dart-fss."""

from __future__ import annotations

import os
from typing import Any

import polars as pl


class DartFssAdapter:
    """Adapter that uses `dart-fss` to fetch detailed financial statements."""

    def __init__(self, api_key: str | None = None, corp_code: str = "00126380"):
        try:
            import dart_fss as dart
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "dart-fss is required for DartFssAdapter. Install with: pip install dart-fss"
            ) from exc

        self.dart = dart
        self.api_key = api_key or os.environ.get("DART_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "DART_API_KEY is required. Get one at https://opendart.fss.or.kr"
            )
        self.corp_code = corp_code
        self._corp: Any | None = None

    def _get_corp(self) -> Any:
        if self._corp is None:
            self.dart.set_api_key(api_key=self.api_key)
            corp_list = self.dart.get_corp_list()
            self._corp = corp_list.find_by_corp_code(self.corp_code)
        return self._corp

    def load_income_statement(
        self,
        period: str | None = None,
        bgn_de: str = "20230101",
    ) -> pl.DataFrame:
        """Fetch consolidated income statement and return a FinFlow DataFrame."""
        corp = self._get_corp()
        fs = corp.extract_fs(bgn_de=bgn_de)
        cis = fs["cis"]
        latest_col = cis.columns[-1] if period is None else period
        df = cis[[latest_col]].reset_index()
        df.columns = ["account", "value"]
        df["value"] = df["value"].astype(float)

        section_map = {
            "매출액": "revenue",
            "영업이익": "operating_income",
            "당기순이익": "profit",
        }
        df["section"] = df["account"].map(section_map)
        df = df.dropna(subset=["section"])

        revenue = float(df.loc[df["section"] == "revenue", "value"].iloc[0])
        operating_income = float(df.loc[df["section"] == "operating_income", "value"].iloc[0])
        net_income = float(df.loc[df["section"] == "profit", "value"].iloc[0])

        rows = [
            {"account": "Revenue", "value": revenue, "section": "revenue"},
            {
                "account": "Operating Expenses",
                "value": -(revenue - operating_income),
                "section": "operating_expenses",
            },
            {"account": "Net Income", "value": net_income, "section": "profit"},
        ]

        result = pl.DataFrame(rows)
        result = result.with_columns(
            pl.lit(str(latest_col)).alias("period"),
            pl.lit("KRW").alias("currency"),
            pl.lit("income_statement").alias("statement"),
        )
        return result
