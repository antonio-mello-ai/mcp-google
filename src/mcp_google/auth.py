"""OAuth2 credential management with multi-account support."""

from __future__ import annotations

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from mcp_google.config import AccountConfig, GoogleConfig

# OAuth scopes required by the tools
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

# In-memory credential cache keyed by email
_credentials_cache: dict[str, Credentials] = {}


def get_credentials(config: GoogleConfig, account: str | None = None) -> Credentials:
    """Return valid OAuth2 credentials for the given account.

    Credentials are cached in memory and auto-refreshed when expired.

    Args:
        config: Google configuration with client ID/secret and accounts.
        account: Email of the account to use. None = default (first) account.

    Returns:
        Valid google.oauth2.credentials.Credentials instance.
    """
    acct: AccountConfig = config.get_account(account)

    if acct.email in _credentials_cache:
        creds = _credentials_cache[acct.email]
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _credentials_cache[acct.email] = creds
            return creds

    creds = Credentials(
        token=None,
        refresh_token=acct.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.client_id,
        client_secret=config.client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    _credentials_cache[acct.email] = creds
    return creds


def clear_cache() -> None:
    """Clear the in-memory credentials cache (useful for testing)."""
    _credentials_cache.clear()
