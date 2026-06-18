"""Financial validation logic."""

from __future__ import annotations

import polars as pl

from .exceptions import (
    CurrencyMismatchError,
    DuplicateAccountError,
    MissingAccountError,
    NullValueError,
    PeriodMismatchError,
    ReconciliationError,
)


class FinancialValidator:
    """Validates financial data before rendering."""

    def __init__(self, statement_type: str):
        self.statement_type = statement_type

    def validate(
        self,
        df: pl.DataFrame,
        required_roles: set[str] | None = None,
        tolerance: float = 0.01,
    ) -> pl.DataFrame:
        """Run all validations."""
        df = self._validate_period(df)
        df = self._validate_currency(df)
        df = self._validate_nulls(df)
        df = self._validate_duplicates(df)

        if required_roles:
            self._validate_required_roles(df, required_roles)

        if self.statement_type == "income_statement":
            self._validate_income_statement(df, tolerance)
        elif self.statement_type == "cash_flow_statement":
            self._validate_cash_flow(df, tolerance)
        elif self.statement_type == "balance_sheet_reconciliation":
            self._validate_balance_sheet(df, tolerance)

        return df

    def _validate_period(self, df: pl.DataFrame) -> pl.DataFrame:
        periods = df["period"].unique().to_list()
        if self.statement_type == "multi_period_comparison":
            if len(periods) != 2:
                raise PeriodMismatchError(
                    periods=periods,
                    context="multi_period_compare()",
                )
            return df
        if len(periods) > 1:
            raise PeriodMismatchError(
                periods=periods,
                context=self.statement_type,
            )
        return df

    def _validate_currency(self, df: pl.DataFrame) -> pl.DataFrame:
        currencies = df["currency"].unique().to_list()
        if len(currencies) > 1:
            raise CurrencyMismatchError(
                currencies=currencies,
                context=self.statement_type,
            )
        return df

    def _validate_nulls(self, df: pl.DataFrame) -> pl.DataFrame:
        required_cols = ["account", "value", "period", "currency"]
        for col in required_cols:
            null_rows = df.filter(df[col].is_null())
            null_count = len(null_rows)
            if null_count > 0:
                accounts = null_rows["account"].unique().to_list()
                raise NullValueError(column=col, accounts=accounts)
        return df

    def _validate_duplicates(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.statement_type == "multi_period_comparison":
            return df
        duplicates = df.filter(df["account"].is_duplicated())["account"].unique().to_list()
        if duplicates:
            raise DuplicateAccountError(accounts=duplicates)
        return df

    def _validate_required_roles(self, df: pl.DataFrame, required_roles: set[str]) -> None:
        # Map detailed sections to aggregate roles for validation
        section_role_map = {
            "current_asset": "asset",
            "non_current_asset": "asset",
            "asset": "asset",
            "current_liability": "liability",
            "non_current_liability": "liability",
            "liability": "liability",
            "equity": "equity",
        }
        available_sections = set(df["section"].drop_nulls().unique().to_list())
        available_roles = {section_role_map.get(s, s) for s in available_sections}
        missing = required_roles - available_roles
        if missing:
            role = list(missing)[0]
            hint_roles = {
                "revenue",
                "profit",
                "beginning_cash",
                "ending_cash",
                "asset",
                "liability",
                "equity",
            }
            section_hint = role if role in hint_roles else None
            raise MissingAccountError(
                role=role,
                statement=self.statement_type,
                available=sorted(available_sections | set(df["account"].unique().to_list())),
                section_hint=section_hint,
            )

    def _validate_income_statement(self, df: pl.DataFrame, tolerance: float) -> None:
        """Validate Revenue + Expenses = Profit relationships.

        Expenses are expected to be negative values, so revenue + expenses = profit.
        """
        revenue = df.filter(df["section"] == "revenue")["value"].sum()
        profit = df.filter(df["section"] == "profit")["value"].sum()

        # Get all expense-like sections (stored as negative values).
        expense_sections = {"cost", "expense", "cost_of_revenue", "operating_expenses", "tax"}
        expenses = df.filter(df["section"].is_in(expense_sections))["value"].sum()

        # Non-operating items can be income or expense; include positive values
        # (income) in the expected profit reconciliation.
        non_op = df.filter(df["section"] == "non_operating_items")
        non_operating_income = 0.0
        if len(non_op) > 0:
            non_operating_income = non_op.filter(non_op["value"] > 0)["value"].sum()

        expected_profit = revenue + expenses + non_operating_income
        diff = abs(expected_profit - profit)

        if diff > tolerance:
            raise ReconciliationError(
                rule="Revenue + Expenses = Net Income",
                expected=expected_profit,
                actual=profit,
                difference=diff,
                period=df["period"][0] if len(df) > 0 else None,
                currency=df["currency"][0] if len(df) > 0 else None,
                tolerance=tolerance,
            )

    def _validate_cash_flow(self, df: pl.DataFrame, tolerance: float) -> None:
        """Validate Beginning Cash + Net Changes = Ending Cash."""
        beginning = df.filter(df["section"] == "beginning_cash")["value"].sum()
        ending = df.filter(df["section"] == "ending_cash")["value"].sum()

        change_sections = {
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "fx_effect",
        }
        net_change = df.filter(df["section"].is_in(change_sections))["value"].sum()

        expected_ending = beginning + net_change
        diff = abs(expected_ending - ending)

        if diff > tolerance:
            raise ReconciliationError(
                rule="Beginning Cash + Net Changes = Ending Cash",
                expected=expected_ending,
                actual=ending,
                difference=diff,
                period=df["period"][0] if len(df) > 0 else None,
                currency=df["currency"][0] if len(df) > 0 else None,
                tolerance=tolerance,
            )

    def _validate_balance_sheet(self, df: pl.DataFrame, tolerance: float) -> None:
        """Validate Assets = Liabilities + Equity."""
        asset_sections = {"asset", "current_asset", "non_current_asset"}
        liability_sections = {"liability", "current_liability", "non_current_liability"}
        equity_sections = {"equity"}

        assets = df.filter(df["section"].is_in(asset_sections))["value"].sum()
        liabilities = df.filter(df["section"].is_in(liability_sections))["value"].sum()
        equity = df.filter(df["section"].is_in(equity_sections))["value"].sum()

        expected_assets = liabilities + equity
        diff = abs(assets - expected_assets)

        if diff > tolerance:
            raise ReconciliationError(
                rule="Assets = Liabilities + Equity",
                expected=expected_assets,
                actual=assets,
                difference=diff,
                period=df["period"][0] if len(df) > 0 else None,
                currency=df["currency"][0] if len(df) > 0 else None,
                tolerance=tolerance,
            )
