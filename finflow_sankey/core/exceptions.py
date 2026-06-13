"""FinFlow Sankey custom exceptions."""


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

    pass


class CurrencyMismatchError(FinFlowError):
    """Raised when multiple currencies are detected."""

    pass


class MissingAccountError(FinFlowError):
    """Raised when a required account role is missing."""

    def __init__(self, role: str, statement: str, available: list[str] | None = None):
        self.role = role
        self.statement = statement
        self.available = available or []
        msg = f"Required role '{role}' is missing for statement '{statement}'."
        if self.available:
            msg += f" Available accounts: {', '.join(self.available)}"
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
        super().__init__(
            f"Reconciliation failed: {rule}\n"
            f"  Expected: {expected:,.2f}\n"
            f"  Actual:   {actual:,.2f}\n"
            f"  Difference: {difference:,.2f}\n"
            f"  Tolerance: {tolerance}"
        )


class NullValueError(FinFlowError):
    """Raised when null values are found in required fields."""

    pass


class DuplicateAccountError(FinFlowError):
    """Raised when duplicate accounts are detected."""

    pass


class InvalidColorError(FinFlowError):
    """Raised when an invalid color is provided."""

    pass


class MissingRoleColorError(FinFlowError):
    """Raised when a required role color is missing from palette."""

    pass


class InvalidOpacityError(FinFlowError):
    """Raised when opacity is out of valid range."""

    pass
