"""Calendar tools — today's events, week agenda, create event."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from googleapiclient.discovery import build

from mcp_google.auth import get_credentials
from mcp_google.config import GoogleConfig
from mcp_google.server import mcp


def _calendar_service(config: GoogleConfig, account: str | None = None):
    """Build an authenticated Google Calendar API service."""
    creds = get_credentials(config, account)
    return build("calendar", "v3", credentials=creds)


def _format_event(event: dict) -> dict:
    """Format a Calendar API event into a clean dict."""
    start = event.get("start", {})
    end = event.get("end", {})
    return {
        "id": event.get("id", ""),
        "summary": event.get("summary", "(no title)"),
        "start": start.get("dateTime", start.get("date", "")),
        "end": end.get("dateTime", end.get("date", "")),
        "location": event.get("location", ""),
        "description": event.get("description", ""),
        "status": event.get("status", ""),
        "html_link": event.get("htmlLink", ""),
    }


def _list_events(
    config: GoogleConfig,
    account: str | None,
    time_min: datetime,
    time_max: datetime,
) -> list[dict]:
    """Fetch events within a time range."""
    service = _calendar_service(config, account)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        )
        .execute()
    )

    return [_format_event(e) for e in result.get("items", [])]


@mcp.tool()
def calendar_today(account: str | None = None) -> list[dict]:
    """Get today's calendar events.

    Args:
        account: Email address of the account to use. Omit for default account.
    """
    config = GoogleConfig.from_env()
    now = datetime.now(tz=UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    return _list_events(config, account, start_of_day, end_of_day)


@mcp.tool()
def calendar_week(account: str | None = None) -> list[dict]:
    """Get this week's calendar events (Monday through Sunday).

    Args:
        account: Email address of the account to use. Omit for default account.
    """
    config = GoogleConfig.from_env()
    now = datetime.now(tz=UTC)
    # Monday of current week
    start_of_week = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = start_of_week + timedelta(days=7)

    return _list_events(config, account, start_of_week, end_of_week)


@mcp.tool()
def calendar_create_event(
    title: str,
    start: str,
    end: str,
    account: str | None = None,
) -> dict:
    """Create a calendar event.

    Args:
        title: Event title/summary.
        start: Start time in ISO 8601 format (e.g. "2025-03-20T10:00:00-03:00").
        end: End time in ISO 8601 format (e.g. "2025-03-20T11:00:00-03:00").
        account: Email address of the account to use. Omit for default account.
    """
    config = GoogleConfig.from_env()
    service = _calendar_service(config, account)

    event_body = {
        "summary": title,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }

    created = service.events().insert(calendarId="primary", body=event_body).execute()

    return _format_event(created)
