"""Gmail tools — list unread, get message, send email."""

from __future__ import annotations

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from mcp_google.auth import get_credentials
from mcp_google.config import GoogleConfig
from mcp_google.server import mcp


def _gmail_service(config: GoogleConfig, account: str | None = None):
    """Build an authenticated Gmail API service."""
    creds = get_credentials(config, account)
    return build("gmail", "v1", credentials=creds)


def _get_header(headers: list[dict], name: str) -> str:
    """Extract a header value by name from Gmail message headers."""
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


@mcp.tool()
def gmail_list_unread(
    account: str | None = None,
    max_results: int = 20,
) -> list[dict]:
    """List unread emails with subject, sender, date, and snippet.

    Args:
        account: Email address of the account to use. Omit for default account.
        max_results: Maximum number of messages to return (default 20, max 100).
    """
    config = GoogleConfig.from_env()
    service = _gmail_service(config, account)
    max_results = min(max(1, max_results), 100)

    result = (
        service.users()
        .messages()
        .list(
            userId="me",
            q="is:unread",
            maxResults=max_results,
        )
        .execute()
    )

    messages = result.get("messages", [])
    if not messages:
        return []

    output = []
    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="metadata")
            .execute()
        )
        headers = msg.get("payload", {}).get("headers", [])
        output.append(
            {
                "id": msg["id"],
                "subject": _get_header(headers, "Subject"),
                "from": _get_header(headers, "From"),
                "date": _get_header(headers, "Date"),
                "snippet": msg.get("snippet", ""),
            }
        )

    return output


@mcp.tool()
def gmail_get_message(
    message_id: str,
    account: str | None = None,
) -> dict:
    """Get full email content by message ID.

    Args:
        message_id: The Gmail message ID (from gmail_list_unread).
        account: Email address of the account to use. Omit for default account.
    """
    config = GoogleConfig.from_env()
    service = _gmail_service(config, account)

    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

    headers = msg.get("payload", {}).get("headers", [])

    # Extract body text
    body = _extract_body(msg.get("payload", {}))

    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId", ""),
        "subject": _get_header(headers, "Subject"),
        "from": _get_header(headers, "From"),
        "to": _get_header(headers, "To"),
        "date": _get_header(headers, "Date"),
        "body": body,
        "labels": msg.get("labelIds", []),
    }


def _extract_body(payload: dict) -> str:
    """Recursively extract plain text body from Gmail message payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    parts = payload.get("parts", [])
    for part in parts:
        # Prefer text/plain
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    # Fallback: try first part recursively
    for part in parts:
        result = _extract_body(part)
        if result:
            return result

    return ""


@mcp.tool()
def gmail_send(
    to: str,
    subject: str,
    body: str,
    account: str | None = None,
) -> dict:
    """Send an email.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain text email body.
        account: Email address of the account to use. Omit for default account.
    """
    config = GoogleConfig.from_env()
    service = _gmail_service(config, account)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")

    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return {
        "id": sent["id"],
        "thread_id": sent.get("threadId", ""),
        "status": "sent",
    }
