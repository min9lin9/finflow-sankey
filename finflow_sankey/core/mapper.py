"""Account mapping from raw account names to standard roles/sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
import yaml


class AccountMapper:
    """Maps raw account names to standard financial statement sections."""

    def __init__(self, mapping: dict[str, list[str]]):
        """
        Args:
            mapping: Dict mapping standard section/role to list of raw account names.
                Example: {"revenue": ["Net Sales", "Sales Revenue"], ...}
        """
        self.mapping = mapping
        self._account_to_section: dict[str, str] = {}
        for section, accounts in mapping.items():
            for account in accounts:
                self._account_to_section[account] = section

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AccountMapper":
        """Load mapping from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(data)

    @classmethod
    def from_dict(cls, mapping: dict[str, Any]) -> "AccountMapper":
        """Load mapping from dict (values may be list or single string)."""
        normalized: dict[str, list[str]] = {}
        for section, accounts in mapping.items():
            if isinstance(accounts, str):
                normalized[section] = [accounts]
            else:
                normalized[section] = list(accounts)
        return cls(normalized)

    def map_account(self, account: str) -> str | None:
        """Return standard section for a raw account name, or None."""
        return self._account_to_section.get(account)

    def apply(self, df: pl.DataFrame, target_col: str = "section") -> pl.DataFrame:
        """Apply mapping to DataFrame.

        Only overwrites target_col when it is null, preserving explicit sections.
        """
        if not self._account_to_section:
            return df

        return df.with_columns(
            pl.when(pl.col(target_col).is_null())
            .then(
                pl.col("account").replace_strict(
                    self._account_to_section,
                    default=None,
                )
            )
            .otherwise(pl.col(target_col))
            .alias(target_col)
        )

    def list_unmapped(self, df: pl.DataFrame) -> list[str]:
        """Return account names that are not covered by the mapping."""
        return (
            df.filter(
                pl.col("section").is_null()
                & pl.col("account").is_not_null()
            )["account"]
            .unique()
            .to_list()
        )
