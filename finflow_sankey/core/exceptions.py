"""FinFlow Sankey custom exceptions."""

from __future__ import annotations


class FinFlowError(Exception):
    """Base exception for FinFlow Sankey."""

    pass


class SchemaError(FinFlowError):
    """Raised when input schema is invalid."""

    pass


class MissingColumnError(SchemaError):
    """Raised when a required column is missing."""

    def __init__(self, column: str):
        self.column = column
        super().__init__(f"Required column '{column}' is missing from input data.")


class PeriodMismatchError(FinFlowError):
    """Raised when multiple periods are detected."""

    def __init__(self, periods: list[str] | None = None, context: str | None = None):
        self.periods = periods or []
        self.context = context
        msg = "Multiple periods detected"
        if context:
            msg += f" for {context}"
        msg += "."
        if self.periods:
            msg += f" Periods found: {', '.join(self.periods)}."
        msg += " Use a single period per Sankey, or use multi_period_compare() for two periods."
        super().__init__(msg)


class CurrencyMismatchError(FinFlowError):
    """Raised when multiple currencies are detected."""

    def __init__(self, currencies: list[str] | None = None, context: str | None = None):
        self.currencies = currencies or []
        self.context = context
        msg = "Multiple currencies detected"
        if context:
            msg += f" for {context}"
        msg += "."
        if self.currencies:
            msg += f" Currencies found: {', '.join(self.currencies)}."
        msg += " Use a single currency per Sankey."
        super().__init__(msg)


class MissingAccountError(FinFlowError):
    """Raised when a required account role is missing."""

    def __init__(
        self,
        role: str,
        statement: str,
        available: list[str] | None = None,
        section_hint: str | None = None,
    ):
        self.role = role
        self.statement = statement
        self.available = available or []
        self.section_hint = section_hint
        msg = f"Required role '{role}' is missing for statement '{statement}'."
        if section_hint:
            msg += f" Expected section: '{section_hint}'."
        if self.available:
            msg += f" Available sections/accounts: {', '.join(self.available[:20])}"
            if len(self.available) > 20:
                msg += f" ... ({len(self.available) - 20} more)"
        msg += " See docs/mapping.md for supported section names."
        super().__init__(msg)


class ReconciliationError(FinFlowError):
    """Raised when financial reconciliation fails."""

    def __init__(
        self,
        rule: str,
        expected: float,
        actual: float,
        difference: float,
        period: str | None = None,
        currency: str | None = None,
        tolerance: float = 0.01,
    ):
        self.rule = rule
        self.expected = expected
        self.actual = actual
        self.difference = difference
        self.period = period
        self.currency = currency
        self.tolerance = tolerance
        ctx = ""
        if period:
            ctx += f" (period: {period})"
        if currency:
            ctx += f" [currency: {currency}]"
        super().__init__(
            f"Reconciliation failed{ctx}: {rule}\n"
            f"  Expected:   {expected:,.4f}\n"
            f"  Actual:     {actual:,.4f}\n"
            f"  Difference: {difference:,.4f}\n"
            f"  Tolerance:  {tolerance}\n"
            f"Check that all sections are included and expense/cost values are negative."
        )


class NullValueError(FinFlowError):
    """Raised when null values are found in required fields."""

    def __init__(self, column: str, accounts: list[str] | None = None):
        self.column = column
        self.accounts = accounts or []
        msg = f"Column '{column}' contains null values."
        if self.accounts:
            account_strs = [str(a) for a in self.accounts[:10]]
            msg += f" Affected accounts: {', '.join(account_strs)}"
            if len(self.accounts) > 10:
                msg += f" ... ({len(self.accounts) - 10} more)"
        super().__init__(msg)


class DuplicateAccountError(FinFlowError):
    """Raised when duplicate accounts are detected."""

    def __init__(self, accounts: list[str] | None = None):
        self.accounts = accounts or []
        msg = "Duplicate account names detected."
        if self.accounts:
            msg += f" Duplicates: {', '.join(self.accounts)}."
        msg += " Account names must be unique within a single period."
        super().__init__(msg)


class InvalidColorError(FinFlowError):
    """Raised when an invalid color is provided."""

    pass


class MissingRoleColorError(FinFlowError):
    """Raised when a required role color is missing from palette."""

    pass


class InvalidOpacityError(FinFlowError):
    """Raised when opacity is out of valid range."""

    pass
