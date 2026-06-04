"""Tests for Gmail and Calendar tools — mocks Google API responses."""

from __future__ import annotations

import base64
import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Set env vars before any import touches GoogleConfig
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["GOOGLE_ACCOUNTS_JSON"] = json.dumps(
    [{"email": "test@gmail.com", "refresh_token": "fake-refresh-token"}]
)

from mcp_google.config import GoogleConfig

# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------


class TestGoogleConfig:
    def test_from_env(self):
        config = GoogleConfig.from_env()
        assert config.client_id == "test-client-id"
        assert config.client_secret == "test-client-secret"
        assert len(config.accounts) == 1
        assert config.accounts[0].email == "test@gmail.com"

    def test_default_account(self):
        config = GoogleConfig.from_env()
        assert config.default_account.email == "test@gmail.com"

    def test_get_account_by_email(self):
        config = GoogleConfig.from_env()
        acct = config.get_account("test@gmail.com")
        assert acct.email == "test@gmail.com"

    def test_get_account_not_found(self):
        config = GoogleConfig.from_env()
        with pytest.raises(ValueError, match="not found"):
            config.get_account("missing@gmail.com")

    def test_missing_client_id(self):
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": ""}):
            with pytest.raises(ValueError, match="GOOGLE_CLIENT_ID"):
                GoogleConfig.from_env()

    def test_invalid_accounts_json(self):
        with patch.dict(os.environ, {"GOOGLE_ACCOUNTS_JSON": "not-json"}):
            with pytest.raises(ValueError, match="not valid JSON"):
                GoogleConfig.from_env()

    def test_empty_accounts_array(self):
        with patch.dict(os.environ, {"GOOGLE_ACCOUNTS_JSON": "[]"}):
            with pytest.raises(ValueError, match="non-empty"):
                GoogleConfig.from_env()


# ---------------------------------------------------------------------------
# Helper to build mock Google services
# ---------------------------------------------------------------------------


def _mock_gmail_service():
    """Return a mock Gmail service with chainable methods."""
    service = MagicMock()
    return service


def _mock_calendar_service():
    """Return a mock Calendar service with chainable methods."""
    service = MagicMock()
    return service


# ---------------------------------------------------------------------------
# Gmail tool tests
# ---------------------------------------------------------------------------


class TestGmailListUnread:
    @patch("mcp_google.tools.gmail._gmail_service")
    def test_returns_unread_messages(self, mock_svc_fn):
        service = _mock_gmail_service()
        mock_svc_fn.return_value = service

        # Mock list response
        service.users().messages().list().execute.return_value = {
            "messages": [{"id": "msg-1"}, {"id": "msg-2"}]
        }

        # Mock get response for each message
        def get_side_effect(userId, id, format):  # noqa: N803 - matches Gmail API kwargs
            mock = MagicMock()
            mock.execute.return_value = {
                "id": id,
                "snippet": f"Snippet for {id}",
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": f"Subject {id}"},
                        {"name": "From", "value": "sender@test.com"},
                        {"name": "Date", "value": "Mon, 1 Jan 2025 10:00:00 +0000"},
                    ]
                },
            }
            return mock

        service.users().messages().get = get_side_effect

        from mcp_google.tools.gmail import gmail_list_unread

        result = gmail_list_unread(max_results=5)

        assert len(result) == 2
        assert result[0]["id"] == "msg-1"
        assert result[0]["subject"] == "Subject msg-1"
        assert result[0]["from"] == "sender@test.com"

    @patch("mcp_google.tools.gmail._gmail_service")
    def test_empty_inbox(self, mock_svc_fn):
        service = _mock_gmail_service()
        mock_svc_fn.return_value = service

        service.users().messages().list().execute.return_value = {"messages": []}

        from mcp_google.tools.gmail import gmail_list_unread

        result = gmail_list_unread()
        assert result == []


class TestGmailGetMessage:
    @patch("mcp_google.tools.gmail._gmail_service")
    def test_returns_full_message(self, mock_svc_fn):
        service = _mock_gmail_service()
        mock_svc_fn.return_value = service

        body_text = "Hello, this is the email body."
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        service.users().messages().get().execute.return_value = {
            "id": "msg-123",
            "threadId": "thread-456",
            "labelIds": ["INBOX", "UNREAD"],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "from@test.com"},
                    {"name": "To", "value": "to@test.com"},
                    {"name": "Date", "value": "Mon, 1 Jan 2025 10:00:00 +0000"},
                ],
                "body": {"data": encoded_body},
            },
        }

        from mcp_google.tools.gmail import gmail_get_message

        result = gmail_get_message(message_id="msg-123")

        assert result["id"] == "msg-123"
        assert result["subject"] == "Test Subject"
        assert result["body"] == body_text


class TestGmailSend:
    @patch("mcp_google.tools.gmail._gmail_service")
    def test_sends_email(self, mock_svc_fn):
        service = _mock_gmail_service()
        mock_svc_fn.return_value = service

        service.users().messages().send().execute.return_value = {
            "id": "sent-msg-1",
            "threadId": "thread-789",
        }

        from mcp_google.tools.gmail import gmail_send

        result = gmail_send(to="recipient@test.com", subject="Hi", body="Hello!")

        assert result["id"] == "sent-msg-1"
        assert result["status"] == "sent"


# ---------------------------------------------------------------------------
# Calendar tool tests
# ---------------------------------------------------------------------------


class TestCalendarToday:
    @patch("mcp_google.tools.calendar._calendar_service")
    def test_returns_today_events(self, mock_svc_fn):
        service = _mock_calendar_service()
        mock_svc_fn.return_value = service

        service.events().list().execute.return_value = {
            "items": [
                {
                    "id": "evt-1",
                    "summary": "Standup",
                    "start": {"dateTime": "2025-01-01T09:00:00-03:00"},
                    "end": {"dateTime": "2025-01-01T09:30:00-03:00"},
                    "status": "confirmed",
                },
                {
                    "id": "evt-2",
                    "summary": "Lunch",
                    "start": {"dateTime": "2025-01-01T12:00:00-03:00"},
                    "end": {"dateTime": "2025-01-01T13:00:00-03:00"},
                    "status": "confirmed",
                },
            ]
        }

        from mcp_google.tools.calendar import calendar_today

        result = calendar_today()

        assert len(result) == 2
        assert result[0]["summary"] == "Standup"
        assert result[1]["summary"] == "Lunch"

    @patch("mcp_google.tools.calendar._calendar_service")
    def test_no_events(self, mock_svc_fn):
        service = _mock_calendar_service()
        mock_svc_fn.return_value = service

        service.events().list().execute.return_value = {"items": []}

        from mcp_google.tools.calendar import calendar_today

        result = calendar_today()
        assert result == []


class TestCalendarWeek:
    @patch("mcp_google.tools.calendar._calendar_service")
    def test_returns_week_events(self, mock_svc_fn):
        service = _mock_calendar_service()
        mock_svc_fn.return_value = service

        service.events().list().execute.return_value = {
            "items": [
                {
                    "id": "evt-w1",
                    "summary": "Monday meeting",
                    "start": {"dateTime": "2025-01-06T10:00:00-03:00"},
                    "end": {"dateTime": "2025-01-06T11:00:00-03:00"},
                    "status": "confirmed",
                }
            ]
        }

        from mcp_google.tools.calendar import calendar_week

        result = calendar_week()

        assert len(result) == 1
        assert result[0]["summary"] == "Monday meeting"


class TestCalendarCreateEvent:
    @patch("mcp_google.tools.calendar._calendar_service")
    def test_creates_event(self, mock_svc_fn):
        service = _mock_calendar_service()
        mock_svc_fn.return_value = service

        service.events().insert().execute.return_value = {
            "id": "new-evt-1",
            "summary": "New Event",
            "start": {"dateTime": "2025-01-15T14:00:00-03:00"},
            "end": {"dateTime": "2025-01-15T15:00:00-03:00"},
            "status": "confirmed",
            "htmlLink": "https://calendar.google.com/event?id=new-evt-1",
        }

        from mcp_google.tools.calendar import calendar_create_event

        result = calendar_create_event(
            title="New Event",
            start="2025-01-15T14:00:00-03:00",
            end="2025-01-15T15:00:00-03:00",
        )

        assert result["id"] == "new-evt-1"
        assert result["summary"] == "New Event"
        assert result["html_link"] != ""
