"""Configuration management — loads Google OAuth settings from environment."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AccountConfig:
    """Single Google account configuration."""

    email: str
    refresh_token: str


@dataclass(frozen=True)
class GoogleConfig:
    """Google API configuration loaded from environment variables."""

    client_id: str
    client_secret: str
    accounts: list[AccountConfig] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> GoogleConfig:
        """Build config from environment variables.

        Required env vars:
            GOOGLE_CLIENT_ID
            GOOGLE_CLIENT_SECRET
            GOOGLE_ACCOUNTS_JSON — JSON array of {"email": "...", "refresh_token": "..."}
        """
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
        accounts_json = os.environ.get("GOOGLE_ACCOUNTS_JSON", "[]")

        if not client_id or not client_secret:
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")

        try:
            raw_accounts = json.loads(accounts_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"GOOGLE_ACCOUNTS_JSON is not valid JSON: {exc}") from exc

        if not isinstance(raw_accounts, list) or not raw_accounts:
            raise ValueError("GOOGLE_ACCOUNTS_JSON must be a non-empty JSON array")

        accounts: list[AccountConfig] = []
        for idx, entry in enumerate(raw_accounts):
            email = entry.get("email")
            refresh_token = entry.get("refresh_token")
            if not email or not refresh_token:
                raise ValueError(f"Account at index {idx} missing 'email' or 'refresh_token'")
            accounts.append(AccountConfig(email=email, refresh_token=refresh_token))

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            accounts=accounts,
        )

    @property
    def default_account(self) -> AccountConfig:
        """Return the first account (default)."""
        return self.accounts[0]

    def get_account(self, email: str | None = None) -> AccountConfig:
        """Resolve account by email, falling back to default."""
        if email is None:
            return self.default_account
        for acct in self.accounts:
            if acct.email == email:
                return acct
        raise ValueError(
            f"Account '{email}' not found. Available: {[a.email for a in self.accounts]}"
        )
